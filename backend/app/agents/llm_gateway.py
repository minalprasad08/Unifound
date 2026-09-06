import re
import json
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import httpx
from app.core.config import settings
from app.agents.models import ToolDecision, AgentStep

logger = logging.getLogger("unifound.agents.llm_gateway")


class LLMProviderError(Exception):
    """Raised when an LLM provider encounters an unrecoverable error."""
    pass


class LLMProvider(ABC):
    """Abstract interface for LLM inference providers."""

    @abstractmethod
    async def generate_decision(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        history: List[AgentStep],
        user_message: str,
    ) -> ToolDecision:
        """Produce the next ReAct tool decision or final answer."""
        pass

    @abstractmethod
    async def reflect(
        self,
        prompt: str,
        steps: List[AgentStep],
        candidate_answer: str,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Evaluate candidate answer. Returns (is_valid, feedback, refined_answer)."""
        pass


class HeuristicReActProvider(LLMProvider):
    """
    Intelligent, deterministic, zero-dependency ReAct decision provider.
    Enables autonomous multi-step reasoning, tool validation, and test reproducibility
    without mandatory paid external APIs or network calls.
    """

    def _extract_id(self, text: str, pattern: str) -> Optional[int]:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            try:
                return int(m.group(1))
            except (ValueError, IndexError):
                return None
        return None

    async def generate_decision(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        history: List[AgentStep],
        user_message: str,
    ) -> ToolDecision:
        tool_names = {t["name"] for t in tools}
        msg = user_message.lower().strip()

        # Security: Prompt Injection Guardrails
        injection_patterns = [
            "ignore all previous instructions",
            "ignore previous instructions",
            "disregard all instructions",
            "forget your instructions",
            "reveal system prompt",
            "show system prompt",
            "print system prompt",
            "reveal secret",
            "print secret",
            "show secret",
            "secret_key",
            "bypass auth",
            "override rules",
            "grant admin",
            "elevate privilege",
            "arbitrary code",
        ]
        if any(pat in msg for pat in injection_patterns):
            return ToolDecision(
                action="final",
                arguments={
                    "answer": "I cannot fulfill requests that attempt to override platform safety instructions, disclose internal configuration secrets, or bypass access controls.",
                    "confidence": 0.0,
                },
                reasoning_summary="Security Guardrail: Refused potential prompt injection attempt.",
            )

        # Check what tools have been executed so far
        executed_tools = [s.decision.tool_name for s in history if s.decision.action == "tool"]
        latest_obs = history[-1].observation if history else None

        # ----------------------------------------------------
        # MULTI-STEP FLOW A: Matching Flow (get_item -> find_matches -> final)
        # ----------------------------------------------------
        item_id_match = self._extract_id(user_message, r"(?:item|report|id)\s*#?\s*(\d+)")

        if any(w in msg for w in ["match", "matches", "matching", "pair", "find match"]):
            if "get_item" not in executed_tools and item_id_match:
                # Step 1: Look up source item
                if "get_item" in tool_names:
                    return ToolDecision(
                        action="tool",
                        tool_name="get_item",
                        arguments={"item_id": item_id_match},
                        reasoning_summary=f"Retrieving source item #{item_id_match} details to evaluate matching candidate criteria.",
                    )

            if "get_item" in executed_tools and "find_matches" not in executed_tools:
                # Step 2: Find matches
                target_id = item_id_match
                if latest_obs and latest_obs.success and "id" in latest_obs.result:
                    target_id = latest_obs.result["id"]

                if target_id and "find_matches" in tool_names:
                    return ToolDecision(
                        action="tool",
                        tool_name="find_matches",
                        arguments={"item_id": target_id, "min_confidence": 40.0},
                        reasoning_summary=f"Running multi-factor matching engine for item #{target_id}.",
                    )

            if "find_matches" in executed_tools:
                # Step 3: Check if top match has an image and we haven't analyzed it yet
                matches_res = None
                for s in history:
                    if s.decision.tool_name == "find_matches" and s.observation and s.observation.success:
                        matches_res = s.observation.result

                if matches_res and matches_res.get("matches"):
                    top = matches_res["matches"][0]
                    cand_id = top.get("item_id")
                    
                    # Synthesize final answer
                    count = matches_res.get("total", len(matches_res["matches"]))
                    conf = top.get("confidence", 0.0)
                    title = top.get("title", "Unknown Item")
                    loc = top.get("location", "Campus")
                    visual_ev = top.get("visual_evidence", [])
                    ev_str = f" Visual evidence: {', '.join(visual_ev)}." if visual_ev else ""

                    answer = (
                        f"Found {count} potential match(es) for item #{matches_res.get('source_item_id')}. "
                        f"The top candidate is #{cand_id}: '{title}' found at {loc} with {conf:.1f}% confidence.{ev_str}"
                    )
                    return ToolDecision(
                        action="final",
                        arguments={"answer": answer, "confidence": conf},
                        reasoning_summary="Successfully evaluated candidate matches and synthesized ranking.",
                    )
                else:
                    return ToolDecision(
                        action="final",
                        arguments={"answer": f"No opposite-type candidate matches were found matching the required confidence threshold.", "confidence": 0.0},
                        reasoning_summary="Matching search completed; no candidates found.",
                    )

        # ----------------------------------------------------
        # FLOW B: Image Analysis Flow
        # ----------------------------------------------------
        if any(w in msg for w in ["analyze image", "inspect image", "visual", "image analysis"]):
            if "analyze_image" not in executed_tools and item_id_match and "analyze_image" in tool_names:
                return ToolDecision(
                    action="tool",
                    tool_name="analyze_image",
                    arguments={"item_id": item_id_match},
                    reasoning_summary=f"Extracting structured visual attributes from image of item #{item_id_match}.",
                )
            if "analyze_image" in executed_tools:
                for s in history:
                    if s.decision.tool_name == "analyze_image" and s.observation:
                        res = s.observation.result
                        if s.observation.success and "image_analysis" in res:
                            ia = res["image_analysis"]
                            colors = ", ".join(ia.get("colors", [])) or "not detected"
                            brand = ia.get("brand") or "Generic"
                            traits = ", ".join(ia.get("characteristics", [])) or "None"
                            conf = ia.get("confidence", 0.9) * 100.0
                            answer = (
                                f"Image analysis for item #{item_id_match} complete: "
                                f"Detected brand: {brand}, Dominant colors: {colors}, "
                                f"Characteristics: {traits} (Visual Confidence: {conf:.1f}%)."
                            )
                            return ToolDecision(
                                action="final",
                                arguments={"answer": answer, "confidence": conf},
                                reasoning_summary="Extracted visual attributes verified and summarized.",
                            )
                        else:
                            err = res.get("error", "Failed to analyze image.")
                            return ToolDecision(
                                action="final",
                                arguments={"answer": f"Could not analyze image for item #{item_id_match}: {err}"},
                                reasoning_summary="Reported image analysis error safely.",
                            )

        # ----------------------------------------------------
        # FLOW C: Claim Creation / Status Flow
        # ----------------------------------------------------
        claim_id_match = self._extract_id(user_message, r"(?:claim|claim\s*id|claim\s*#)\s*(\d+)")

        if any(w in msg for w in ["claim status", "check claim", "my claim"]) and claim_id_match:
            if "get_claim_status" not in executed_tools and "get_claim_status" in tool_names:
                return ToolDecision(
                    action="tool",
                    tool_name="get_claim_status",
                    arguments={"claim_id": claim_id_match},
                    reasoning_summary=f"Checking status for claim #{claim_id_match}.",
                )
            if "get_claim_status" in executed_tools:
                for s in history:
                    if s.decision.tool_name == "get_claim_status" and s.observation:
                        res = s.observation.result
                        if s.observation.success and "status" in res:
                            status = res.get("status")
                            item_title = res.get("item_title", f"item #{res.get('item_id')}")
                            return ToolDecision(
                                action="final",
                                arguments={"answer": f"Claim #{claim_id_match} for '{item_title}' is currently in status: {status}."},
                                reasoning_summary="Retrieved and verified claim status.",
                            )
                        else:
                            err = res.get("error", "Claim not found.")
                            return ToolDecision(
                                action="final",
                                arguments={"answer": f"Unable to retrieve claim #{claim_id_match}: {err}"},
                                reasoning_summary="Reported claim retrieval error.",
                            )

        if any(w in msg for w in ["submit claim", "claim this", "create claim", "file claim"]) and item_id_match:
            if "create_claim" not in executed_tools and "create_claim" in tool_names:
                desc = "I lost this item and have proof of ownership."
                # Extract descriptive text if available
                desc_match = re.search(r'(?:description|reason|because)[:\s]+([^.]+)', user_message, re.IGNORECASE)
                if desc_match:
                    desc = desc_match.group(1).strip()
                if len(desc) < 10:
                    desc = "Claiming lost campus property with verified ownership proof."

                return ToolDecision(
                    action="tool",
                    tool_name="create_claim",
                    arguments={"item_id": item_id_match, "description": desc},
                    reasoning_summary=f"Submitting ownership claim for item #{item_id_match} using authenticated identity.",
                )
            if "create_claim" in executed_tools:
                for s in history:
                    if s.decision.tool_name == "create_claim" and s.observation:
                        res = s.observation.result
                        if s.observation.success and "claim_id" in res:
                            cid = res["claim_id"]
                            st = res["status"]
                            return ToolDecision(
                                action="final",
                                arguments={"answer": f"Ownership claim #{cid} for item #{item_id_match} has been submitted successfully with status {st}."},
                                reasoning_summary="Confirmed claim creation.",
                            )
                        else:
                            err = res.get("error", "Claim failed.")
                            return ToolDecision(
                                action="final",
                                arguments={"answer": f"Could not submit claim for item #{item_id_match}: {err}"},
                                reasoning_summary="Reported claim failure safely.",
                            )

        # ----------------------------------------------------
        # FLOW D: Item Search Flow (search_items -> final)
        # ----------------------------------------------------
        if "search_items" not in executed_tools:
            # Extract keywords or item type
            item_type = None
            if "lost" in msg:
                item_type = "LOST"
            elif "found" in msg:
                item_type = "FOUND"

            # Filter out common stop-words
            cleaned = re.sub(r'\b(find|search|for|my|the|a|an|i|lost|found|is|there|any|item|items)\b', '', user_message, flags=re.IGNORECASE)
            keyword = cleaned.strip() or None

            if "search_items" in tool_names:
                return ToolDecision(
                    action="tool",
                    tool_name="search_items",
                    arguments={"keyword": keyword, "item_type": item_type, "page": 1, "page_size": 5},
                    reasoning_summary=f"Searching items with keyword='{keyword}' and type='{item_type}'.",
                )

        if "search_items" in executed_tools:
            for s in history:
                if s.decision.tool_name == "search_items" and s.observation:
                    res = s.observation.result
                    if s.observation.success and "items" in res:
                        items = res["items"]
                        count = res.get("total", len(items))
                        if count == 0:
                            return ToolDecision(
                                action="final",
                                arguments={"answer": f"No items matching your search criteria were found in the UniFound registry."},
                                reasoning_summary="Search yielded no results.",
                            )
                        summaries = [f"#{it['id']} '{it['title']}' ({it['item_type']}, {it['location']}, Status: {it['status']})" for it in items[:3]]
                        answer = f"Found {count} item(s) matching your request:\n" + "\n".join(summaries)
                        return ToolDecision(
                            action="final",
                            arguments={"answer": answer},
                            reasoning_summary="Synthesized search results.",
                        )

        # Fallback default final response
        return ToolDecision(
            action="final",
            arguments={"answer": "I have processed your inquiry based on UniFound campus records."},
            reasoning_summary="Standard final resolution.",
        )

    async def reflect(
        self,
        prompt: str,
        steps: List[AgentStep],
        candidate_answer: str,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        # Check if observations contain failures that the candidate claims succeeded
        for s in steps:
            if s.observation and not s.observation.success:
                err_msg = s.observation.result.get("error", "")
                if "success" in candidate_answer.lower() and err_msg.lower() not in candidate_answer.lower():
                    return False, f"Step {s.step_number} encountered an error '{err_msg}', but the final answer incorrectly described success.", None

        # Check for hallucinated confidence without matches tool
        has_matches_tool = any(s.decision.tool_name in ("find_matches", "analyze_image") for s in steps)
        if not has_matches_tool and re.search(r'\b(9\d|100)%\s*confidence\b', candidate_answer):
            return False, "Candidate answer claims high confidence without calling matching or image analysis tools.", None

        return True, None, None


class GeminiLLMProvider(LLMProvider):
    """External Google Gemini API provider."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", timeout: int = 15):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    async def generate_decision(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        history: List[AgentStep],
        user_message: str,
    ) -> ToolDecision:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(text)
            return ToolDecision(**parsed)

    async def reflect(
        self,
        prompt: str,
        steps: List[AgentStep],
        candidate_answer: str,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(text)
            return parsed.get("is_valid", True), parsed.get("feedback"), parsed.get("refined_answer")


class LLMGateway:
    """
    Gateway that routes queries to primary provider with transparent fallback.
    Handles network errors, malformed outputs, and timeouts safely.
    """

    def __init__(
        self,
        primary_provider: Optional[LLMProvider] = None,
        fallback_provider: Optional[LLMProvider] = None,
        timeout: Optional[int] = None,
    ):
        self.timeout = timeout or settings.LLM_REQUEST_TIMEOUT
        self.fallback = fallback_provider or HeuristicReActProvider()

        if primary_provider:
            self.primary = primary_provider
        elif settings.LLM_PROVIDER == "gemini" and settings.LLM_API_KEY:
            self.primary = GeminiLLMProvider(
                api_key=settings.LLM_API_KEY,
                model=settings.LLM_MODEL,
                timeout=self.timeout,
            )
        else:
            self.primary = self.fallback

    async def generate_decision(
        self,
        prompt: str,
        tools: List[Dict[str, Any]],
        history: List[AgentStep],
        user_message: str,
    ) -> ToolDecision:
        """Call primary provider with timeout, falling back automatically if needed."""
        try:
            return await asyncio.wait_for(
                self.primary.generate_decision(prompt, tools, history, user_message),
                timeout=self.timeout,
            )
        except Exception as e:
            logger.warning("Primary LLM provider failed (%s). Falling back to heuristic provider.", e)
            return await self.fallback.generate_decision(prompt, tools, history, user_message)

    async def reflect(
        self,
        prompt: str,
        steps: List[AgentStep],
        candidate_answer: str,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Call reflection validator with fallback."""
        try:
            return await asyncio.wait_for(
                self.primary.reflect(prompt, steps, candidate_answer),
                timeout=self.timeout,
            )
        except Exception as e:
            logger.warning("Primary LLM reflection failed (%s). Falling back to heuristic validator.", e)
            return await self.fallback.reflect(prompt, steps, candidate_answer)
