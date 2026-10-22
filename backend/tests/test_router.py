import sys
import os
sys.path = [p for p in sys.path if not p.lower().rstrip('\\/').endswith('desktop')]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))
sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app.schemas import ProcessingRoute, ChatRequest
from app.agent.decider_adapter import decider_adapter
from app.agent.orchestrator import orchestrator
from app.evaluation.benchmark import benchmark_runner


def test_lightweight_routing():
    """Verify factual, simple queries are classified as LIGHTWEIGHT."""
    decision = decider_adapter.decide("What is the capital of France?")
    assert decision.route == ProcessingRoute.LIGHTWEIGHT
    assert decision.confidence is not None
    assert decision.confidence >= 0.70

def test_advanced_routing():
    """Verify complex systems queries are classified as ADVANCED."""
    decision = decider_adapter.decide(
        "Design a high-throughput distributed event streaming architecture on AWS with multi-region active-active failover."
    )
    assert decision.route == ProcessingRoute.ADVANCED
    assert decision.confidence is not None
    assert decision.confidence >= 0.75

def test_ambiguous_routing():
    """Verify zero-context queries trigger CLARIFY route."""
    decision = decider_adapter.decide("Fix it.")
    assert decision.route == ProcessingRoute.CLARIFY
    assert decision.confidence is not None

def test_orchestrator_end_to_end_clarify():
    """Verify end-to-end pipeline handles clarification without invoking LLMs."""
    req = ChatRequest(prompt="Run the script.")
    res = orchestrator.process_request(req)
    assert res.route == ProcessingRoute.CLARIFY
    assert "clarify" in res.response.lower() or "details" in res.response.lower()

def test_orchestrator_forced_route():
    """Verify forced route override."""
    req = ChatRequest(prompt="Hello there", force_route=ProcessingRoute.ADVANCED)
    res = orchestrator.process_request(req)
    assert res.route == ProcessingRoute.ADVANCED
    assert res.decision.is_fallback is False

def test_benchmark_metrics_calculation():
    """Verify benchmark executes and produces valid comparative metrics."""
    res = benchmark_runner.run_benchmark(sample_limit=3)
    assert res.sample_count == 3
    assert res.decider_results.total_samples == 3
    assert res.baseline_results.total_samples == 3
    assert res.decider_results.avg_decision_latency_ms < res.baseline_results.avg_decision_latency_ms
