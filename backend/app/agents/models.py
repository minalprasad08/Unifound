from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """User input prompt submitted to the ReAct agent."""
    message: str = Field(..., min_length=1, max_length=2000, description="Natural language query or request for the lost and found agent.")


class ToolDecision(BaseModel):
    """Structured decision taken by the LLM in a single ReAct step."""
    action: Literal["tool", "final"] = Field(..., description="Action type: 'tool' to call an MCP tool, or 'final' to finish.")
    tool_name: Optional[str] = Field(None, description="Name of the MCP tool to execute if action is 'tool'.")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Typed arguments to pass to the MCP tool.")
    reasoning_summary: Optional[str] = Field(None, description="Concise safe rationale for this step (excludes private chain-of-thought).")


class ToolObservation(BaseModel):
    """Structured observation returned from an MCP tool execution."""
    tool_name: str = Field(..., description="Name of the executed MCP tool.")
    arguments: Dict[str, Any] = Field(..., description="Arguments passed to the tool.")
    result: Dict[str, Any] = Field(..., description="Structured response received from the MCP tool.")
    success: bool = Field(True, description="Whether the tool executed without error.")


class AgentStep(BaseModel):
    """A single execution step in the ReAct loop."""
    step_number: int = Field(..., ge=1, description="Sequential step index (1-indexed).")
    decision: ToolDecision = Field(..., description="LLM decision taken for this step.")
    observation: Optional[ToolObservation] = Field(None, description="Observation produced by tool execution.")


class AgentResponse(BaseModel):
    """Final verified response returned by the ReAct orchestrator."""
    final_answer: str = Field(..., description="Synthesized, factual final answer to the user query.")
    tools_used: List[str] = Field(default_factory=list, description="List of unique MCP tool names executed.")
    steps_count: int = Field(..., ge=0, description="Total number of ReAct loop iterations taken.")
    execution_status: str = Field(..., description="Execution status: 'COMPLETED', 'MAX_ITERATIONS', or 'FAILED'.")
    confidence: Optional[float] = Field(None, ge=0.0, le=100.0, description="Confidence score if applicable (e.g. from match candidate).")
    tool_results_summary: List[Dict[str, Any]] = Field(default_factory=list, description="High-level sanitized summary of key tool results.")
