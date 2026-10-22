from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ProcessingRoute(str, Enum):
    LIGHTWEIGHT = "LIGHTWEIGHT"
    ADVANCED = "ADVANCED"
    CLARIFY = "CLARIFY"

class RoutingReason(str, Enum):
    DECIDER_CONFIDENT = "DECIDER_CONFIDENT"
    LOW_CONFIDENCE_FALLBACK = "LOW_CONFIDENCE_FALLBACK"
    AMBIGUITY_DETECTED = "AMBIGUITY_DETECTED"
    DECIDER_SERVICE_ERROR = "DECIDER_SERVICE_ERROR"
    DETERMINISTIC_FAST_PATH = "DETERMINISTIC_FAST_PATH"
    BASELINE_EVAL = "BASELINE_EVAL"

# Request Schemas
class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=16000, description="User prompt to process")
    force_route: Optional[ProcessingRoute] = Field(None, description="Optional override for testing routes")
    strategy: Optional[str] = Field("decider", description="'decider' or 'baseline'")

class RoutingDecision(BaseModel):
    route: ProcessingRoute
    confidence: Optional[float] = Field(None, description="Calibrated confidence returned by Decider 2B or Bedrock baseline")
    raw_choice: str
    decision_latency_ms: float
    reason: RoutingReason
    is_fallback: bool = False
    decision_question: str
    allowed_choices: List[str]
    model_name: str

class ChatResponse(BaseModel):
    request_id: str
    response: str
    route: ProcessingRoute
    model_used: str
    is_demo: bool
    decision: RoutingDecision
    total_latency_ms: float
    tokens_estimated: Optional[int] = None
    cost_estimated_usd: Optional[float] = None
    timestamp: str

# Analytics Schemas
class RouteStats(BaseModel):
    lightweight_count: int = 0
    advanced_count: int = 0
    clarify_count: int = 0
    fallback_count: int = 0
    total_requests: int = 0

class LatencyStats(BaseModel):
    p50_decision_ms: float = 0.0
    p95_decision_ms: float = 0.0
    avg_decision_ms: float = 0.0
    avg_total_ms: float = 0.0

class AnalyticsResponse(BaseModel):
    total_requests: int
    routes: RouteStats
    latency: LatencyStats
    estimated_savings_pct: float
    accuracy_eval_pct: Optional[float] = None
    system_status: Dict[str, Any]

# History Schemas
class HistoryItem(BaseModel):
    request_id: str
    timestamp: str
    prompt_preview: str
    route: ProcessingRoute
    model_used: str
    confidence: Optional[float]
    decision_latency_ms: float
    total_latency_ms: float
    is_fallback: bool
    is_demo: bool

# Benchmark Schemas
class BenchmarkCase(BaseModel):
    id: str
    prompt: str
    expected_route: ProcessingRoute
    description: str

class BenchmarkComparisonResult(BaseModel):
    strategy: str # "Decider 2B" or "Bedrock Baseline"
    total_samples: int
    accuracy_pct: float
    avg_decision_latency_ms: float
    p50_decision_latency_ms: float
    p95_decision_latency_ms: float
    avg_total_latency_ms: float
    estimated_routing_cost_usd: Optional[float]
    model_invocations_for_routing: int
    error_count: int

class BenchmarkResponse(BaseModel):
    run_id: str
    sample_count: int
    timestamp: str
    decider_results: BenchmarkComparisonResult
    baseline_results: BenchmarkComparisonResult
    latency_reduction_pct: float
    notes: List[str]
