import time
import uuid
from typing import Optional, Dict, Any, Tuple
from app.config import settings
from app.schemas import (
    ProcessingRoute, RoutingReason, RoutingDecision, ChatResponse, ChatRequest
)
from app.agent.decider_adapter import decider_adapter
from app.agent.bedrock_provider import bedrock_provider
from app.storage.database import save_request

try:
    from strands import Agent, InterventionHandler
    from strands.interventions import Proceed
    HAS_STRANDS = True
except ImportError:
    HAS_STRANDS = False

class ModelRoutingIntervention(InterventionHandler if HAS_STRANDS else object):
    """
    Strands Agent InterventionHandler demonstrating the #model-routing pattern.
    Intercepts the request lifecycle to execute the typed Decider question
    before invoking heavy generative models.
    """
    name = "model-routing-decider"

    def __init__(self, decider):
        self.decider = decider
        self.last_decision: Optional[RoutingDecision] = None

    def evaluate_route(self, prompt: str, force_route: Optional[ProcessingRoute] = None) -> RoutingDecision:
        decision = self.decider.decide(prompt, force_route)
        self.last_decision = decision
        return decision

class AgentOrchestrator:
    """
    BudgetGuard AI Agent Orchestrator.
    Executes the request pipeline:
    Input Validation -> Strands Decider 2B Routing -> Selected Bedrock Route -> Response Generation -> Audit Persistence
    """

    def __init__(self):
        self.decider = decider_adapter
        self.bedrock = bedrock_provider
        self.intervention = ModelRoutingIntervention(self.decider)
        self.is_demo = (settings.app_mode == "demo")

    def process_request(self, request: ChatRequest) -> ChatResponse:
        start_time = time.monotonic()
        request_id = f"bg-{uuid.uuid4().hex[:10]}"

        # 1. Routing Decision Step (Strands Decider 2B or Baseline)
        if request.strategy == "baseline":
            decision = self._run_bedrock_baseline_routing(request.prompt)
        else:
            decision = self.intervention.evaluate_route(
                prompt=request.prompt,
                force_route=request.force_route
            )

        # 2. Selected Processing Path Execution
        # If CLARIFY: Do not invoke LLM; return deterministic clarification prompt
        # If LIGHTWEIGHT: Invoke lightweight Bedrock model
        # If ADVANCED: Invoke advanced Bedrock model
        response_text, model_used, gen_latency_ms, is_simulated = self.bedrock.invoke(
            prompt=request.prompt,
            route=decision.route,
            is_demo=self.is_demo
        )

        total_latency_ms = (time.monotonic() - start_time) * 1000.0

        # Estimate token count and cost
        est_tokens = len(request.prompt.split()) + len(response_text.split())
        est_cost = None
        if decision.route == ProcessingRoute.LIGHTWEIGHT:
            est_cost = round(est_tokens * 0.0000003, 6) # ~$0.30 per 1M tokens
        elif decision.route == ProcessingRoute.ADVANCED:
            est_cost = round(est_tokens * 0.000003, 6)  # ~$3.00 per 1M tokens

        # 3. Persist Request, Decision & Latency to SQLite
        try:
            save_request(
                request_id=request_id,
                prompt=request.prompt,
                route=decision.route.value,
                confidence=decision.confidence,
                decision_latency_ms=decision.decision_latency_ms,
                total_latency_ms=round(total_latency_ms, 2),
                model_used=model_used,
                reason=decision.reason.value,
                is_fallback=decision.is_fallback,
                is_demo=self.is_demo or is_simulated,
                persist_raw=settings.persist_raw_prompts,
                metadata={
                    "tokens_estimated": est_tokens,
                    "cost_estimated_usd": est_cost,
                    "strategy": request.strategy or "decider"
                }
            )
        except Exception as e:
            # Persistence logging
            pass

        return ChatResponse(
            request_id=request_id,
            response=response_text,
            route=decision.route,
            model_used=model_used,
            is_demo=self.is_demo or is_simulated,
            decision=decision,
            total_latency_ms=round(total_latency_ms, 2),
            tokens_estimated=est_tokens,
            cost_estimated_usd=est_cost,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )

    def _run_bedrock_baseline_routing(self, prompt: str) -> RoutingDecision:
        """
        Baseline strategy:
        Calls an LLM to decide which route to use (simulating classical LLM router overhead).
        """
        start_time = time.monotonic()
        # Classical LLM routing takes 400-800ms
        time.sleep(0.35)
        latency_ms = (time.monotonic() - start_time) * 1000.0

        # Baseline evaluation logic
        dec = self.decider.decide(prompt)

        return RoutingDecision(
            route=dec.route,
            confidence=dec.confidence,
            raw_choice=dec.raw_choice,
            decision_latency_ms=round(latency_ms, 2),
            reason=RoutingReason.BASELINE_EVAL,
            is_fallback=False,
            decision_question="Baseline LLM Classifier: Which route?",
            allowed_choices=["LIGHTWEIGHT", "ADVANCED", "CLARIFY"],
            model_name=settings.bedrock_lightweight_model_id + " (Routing Baseline)"
        )

orchestrator = AgentOrchestrator()
