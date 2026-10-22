from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ProcessingRoute(str, Enum):
    LIGHTWEIGHT = "LIGHTWEIGHT"
    ADVANCED = "ADVANCED"
    CLARIFY = "CLARIFY"


class DecisionQuestion(BaseModel):
    """
    Contract for typed decision questions posed to Strands Decider 2B or Bedrock baseline.
    """
    question: str = "Which processing route is appropriate for this request?"
    choices: List[str] = [
        ProcessingRoute.LIGHTWEIGHT.value,
        ProcessingRoute.ADVANCED.value,
        ProcessingRoute.CLARIFY.value
    ]
    instructions: str = (
        "Evaluate the incoming request state. "
        "Select LIGHTWEIGHT if the request is straightforward, factual, translation, or simple formatting. "
        "Select ADVANCED if the request requires deep reasoning, architectural design, complex code, or multi-step logic. "
        "Select CLARIFY if the request lacks essential context, is underspecified, or too ambiguous to execute safely."
    )
    criteria: Dict[str, str] = {
        ProcessingRoute.LIGHTWEIGHT.value: "Direct factual questions, simple translations, grammar edits, single-step formatting.",
        ProcessingRoute.ADVANCED.value: "Multi-layered logic, system design, software engineering implementations, algorithmic analysis.",
        ProcessingRoute.CLARIFY.value: "Ambiguous, missing context, under-specified commands, uncertain targets."
    }

MODEL_ROUTING_QUESTION = DecisionQuestion()
