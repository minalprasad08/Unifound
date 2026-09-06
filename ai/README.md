# UniFound AI Module

This module houses the AI-powered matching engine, multimodal item feature extraction, and multi-agent systems.

## Planned Components (Phases 4 & 6)
- `matching_engine/`: Multi-factor attribute, location, temporal, and semantic similarity scorer with explainability breakdown.
- `agents/`:
  - `orchestrator.py`: Multi-agent ReAct loop coordinating tool execution.
  - `matching_agent.py`: Specialized agent for identifying potential lost-found pairings.
  - `claim_agent.py`: Claim consistency and evidence analysis.
  - `reflection_agent.py`: Validation and response safety review.
