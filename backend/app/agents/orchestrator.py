import time
import logging
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.mcp.client import UniFoundMCPClient
from app.mcp.context import MCPAuthContext
from app.agents.models import (
    ToolDecision,
    ToolObservation,
    AgentStep,
    AgentResponse,
)
from app.agents.prompts import build_react_prompt
from app.agents.llm_gateway import LLMGateway
from app.agents.reflection import ReflectionAgent

logger = logging.getLogger("unifound.agents.orchestrator")


class ReActOrchestrator:
    """
    ReAct-style Agentic AI Orchestrator.
    Communicates with UniFound system functions EXCLUSIVELY through UniFoundMCPClient.
    Never directly queries databases, SQLAlchemy models, or repositories.
    """

    def __init__(
        self,
        mcp_client: Optional[UniFoundMCPClient] = None,
        llm_gateway: Optional[LLMGateway] = None,
        max_iterations: Optional[int] = None,
        total_timeout: float = 30.0,
    ):
        self.mcp_client = mcp_client or UniFoundMCPClient()
        self.llm_gateway = llm_gateway or LLMGateway()
        self.reflection = ReflectionAgent(self.llm_gateway)
        self.max_iterations = max_iterations or settings.AGENT_MAX_ITERATIONS
        self.total_timeout = total_timeout

    async def run(
        self,
        message: str,
        auth_context: MCPAuthContext,
    ) -> AgentResponse:
        """
        Execute the autonomous ReAct loop for a user query with authenticated MCP context.
        """
        start_time = time.time()
        logger.info("Agent query initiated by user %s: '%s'", auth_context.user_id, message)

        # 1. Dynamically discover available MCP tools
        if not self.mcp_client.is_connected:
            await self.mcp_client.connect()

        tools = await self.mcp_client.list_tools()
        valid_tool_names = {t["name"] for t in tools}

        steps: List[AgentStep] = []
        tools_used: List[str] = []
        reflection_corrected = False
        reflection_feedback: Optional[str] = None
        final_answer: Optional[str] = None
        extracted_confidence: Optional[float] = None
        execution_status = "COMPLETED"

        for iteration in range(1, self.max_iterations + 1):
            # Check total execution timeout
            if time.time() - start_time > self.total_timeout:
                logger.warning("Agent execution exceeded total timeout limit (%ss)", self.total_timeout)
                execution_status = "FAILED"
                final_answer = f"Agent processing timed out after {self.total_timeout:.0f} seconds."
                break

            # 2. Build prompt with dynamic tools & execution history
            prompt = build_react_prompt(
                query=message,
                tools=tools,
                steps=steps,
                feedback=reflection_feedback,
            )
            reflection_feedback = None  # reset feedback after applying

            # 3. LLM decides next action
            try:
                decision: ToolDecision = await self.llm_gateway.generate_decision(
                    prompt=prompt,
                    tools=tools,
                    history=steps,
                    user_message=message,
                )
            except Exception as e:
                logger.error("LLM decision generation failed: %s", e)
                execution_status = "FAILED"
                final_answer = "I encountered an error processing your request. Please try again."
                break

            # 4. Check if LLM decided final answer
            if decision.action == "final":
                candidate_answer = decision.arguments.get("answer", "Inquiry processed.")
                if "confidence" in decision.arguments:
                    extracted_confidence = float(decision.arguments["confidence"])

                # 5. Run Reflection verification
                is_valid, feedback, refined = await self.reflection.validate(
                    query=message,
                    steps=steps,
                    candidate_answer=candidate_answer,
                )

                if is_valid:
                    final_answer = refined or candidate_answer
                    steps.append(AgentStep(step_number=iteration, decision=decision))
                    break
                elif not reflection_corrected:
                    # Allow 1 corrective iteration
                    logger.info("Reflection failed. Triggering 1 corrective ReAct iteration: %s", feedback)
                    reflection_corrected = True
                    reflection_feedback = feedback
                    steps.append(AgentStep(step_number=iteration, decision=decision))
                    continue
                else:
                    # Already attempted corrective iteration, apply safe fallback
                    final_answer = refined or candidate_answer
                    steps.append(AgentStep(step_number=iteration, decision=decision))
                    break

            # 6. Action is 'tool' - Validate tool name against dynamically discovered MCP catalog
            tool_name = decision.tool_name
            if not tool_name or tool_name not in valid_tool_names:
                obs_err = {
                    "error": f"Tool '{tool_name}' is not available. Please choose from: {', '.join(valid_tool_names)}",
                    "code": "UNKNOWN_TOOL",
                }
                obs = ToolObservation(
                    tool_name=tool_name or "unknown",
                    arguments=decision.arguments,
                    result=obs_err,
                    success=False,
                )
                steps.append(AgentStep(step_number=iteration, decision=decision, observation=obs))
                continue

            # 7. Execute tool strictly via MCP Client
            if tool_name not in tools_used:
                tools_used.append(tool_name)

            try:
                tool_res = await self.mcp_client.call_tool(
                    tool_name=tool_name,
                    arguments=decision.arguments,
                    auth_context=auth_context,
                )
                is_err = "error" in tool_res and ("code" in tool_res or tool_res.get("error"))
                obs = ToolObservation(
                    tool_name=tool_name,
                    arguments=decision.arguments,
                    result=tool_res,
                    success=not is_err,
                )

                # Track confidence if returned by matching tool
                if tool_name == "find_matches" and "matches" in tool_res and tool_res["matches"]:
                    extracted_confidence = tool_res["matches"][0].get("confidence")

            except Exception as e:
                logger.error("Error during MCP tool execution '%s': %s", tool_name, e)
                obs = ToolObservation(
                    tool_name=tool_name,
                    arguments=decision.arguments,
                    result={"error": str(e), "code": "MCP_CALL_FAILED"},
                    success=False,
                )

            steps.append(AgentStep(step_number=iteration, decision=decision, observation=obs))

        # Handle max iteration limit exceeded
        if final_answer is None:
            execution_status = "MAX_ITERATIONS"
            final_answer = (
                f"Reached the maximum search limit ({self.max_iterations} steps) while processing your inquiry. "
                f"Executed tools: {', '.join(tools_used) or 'none'}."
            )

        # Build sanitized tool results summary
        results_summary = []
        for s in steps:
            if s.observation:
                results_summary.append({
                    "step": s.step_number,
                    "tool": s.observation.tool_name,
                    "success": s.observation.success,
                    "summary": str(s.observation.result)[:200],
                })

        duration = time.time() - start_time
        logger.info("Agent query completed in %.2fs. Status=%s, Steps=%d", duration, execution_status, len(steps))

        return AgentResponse(
            final_answer=final_answer,
            tools_used=tools_used,
            steps_count=len(steps),
            execution_status=execution_status,
            confidence=extracted_confidence,
            tool_results_summary=results_summary,
        )
