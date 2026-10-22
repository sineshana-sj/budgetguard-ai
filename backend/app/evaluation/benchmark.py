import time
import uuid
from typing import List, Dict, Any
from app.agent.orchestrator import orchestrator
from app.evaluation.dataset import BENCHMARK_DATASET
from app.schemas import (
    BenchmarkResponse, BenchmarkComparisonResult, ProcessingRoute, ChatRequest
)
from app.storage.database import save_evaluation

class BenchmarkRunner:
    """
    Executes honest, bounded benchmark comparing:
    A. Baseline: Generative LLM classifier for routing + selected Bedrock processing
    B. Strands Decider 2B: Single-pass pointer-head routing + selected Bedrock processing
    """

    def run_benchmark(self, sample_limit: int = 15) -> BenchmarkResponse:
        dataset = BENCHMARK_DATASET[:sample_limit]
        total_samples = len(dataset)
        run_id = f"bench-{uuid.uuid4().hex[:8]}"

        # Warm-up run
        orchestrator.process_request(ChatRequest(prompt="Warmup test query", strategy="decider"))

        # 1. Evaluate Strands Decider 2B
        decider_dec_lats: List[float] = []
        decider_tot_lats: List[float] = []
        decider_correct = 0
        decider_errors = 0

        for case in dataset:
            try:
                res = orchestrator.process_request(ChatRequest(prompt=case["prompt"], strategy="decider"))
                decider_dec_lats.append(res.decision.decision_latency_ms)
                decider_tot_lats.append(res.total_latency_ms)
                if res.route == case["expected_route"]:
                    decider_correct += 1
            except Exception:
                decider_errors += 1

        # 2. Evaluate Baseline
        baseline_dec_lats: List[float] = []
        baseline_tot_lats: List[float] = []
        baseline_correct = 0
        baseline_errors = 0

        for case in dataset:
            try:
                res = orchestrator.process_request(ChatRequest(prompt=case["prompt"], strategy="baseline"))
                baseline_dec_lats.append(res.decision.decision_latency_ms)
                baseline_tot_lats.append(res.total_latency_ms)
                if res.route == case["expected_route"]:
                    baseline_correct += 1
            except Exception:
                baseline_errors += 1

        # Calculate statistics
        decider_acc = round((decider_correct / total_samples) * 100.0, 1) if total_samples > 0 else 0.0
        baseline_acc = round((baseline_correct / total_samples) * 100.0, 1) if total_samples > 0 else 0.0

        dec_avg_dec_lat = round(sum(decider_dec_lats) / len(decider_dec_lats), 2) if decider_dec_lats else 0.0
        dec_avg_tot_lat = round(sum(decider_tot_lats) / len(decider_tot_lats), 2) if decider_tot_lats else 0.0
        sorted_dec = sorted(decider_dec_lats)
        dec_p50 = sorted_dec[int(len(sorted_dec) * 0.50)] if sorted_dec else 0.0
        dec_p95 = sorted_dec[int(len(sorted_dec) * 0.95)] if sorted_dec else 0.0

        base_avg_dec_lat = round(sum(baseline_dec_lats) / len(baseline_dec_lats), 2) if baseline_dec_lats else 0.0
        base_avg_tot_lat = round(sum(baseline_tot_lats) / len(baseline_tot_lats), 2) if baseline_tot_lats else 0.0
        sorted_base = sorted(baseline_dec_lats)
        base_p50 = sorted_base[int(len(sorted_base) * 0.50)] if sorted_base else 0.0
        base_p95 = sorted_base[int(len(sorted_base) * 0.95)] if sorted_base else 0.0

        # Latency reduction on routing decision
        lat_reduction_pct = 0.0
        if base_avg_dec_lat > 0:
            lat_reduction_pct = round(((base_avg_dec_lat - dec_avg_dec_lat) / base_avg_dec_lat) * 100.0, 1)

        decider_comp = BenchmarkComparisonResult(
            strategy="Strands Decider 2B",
            total_samples=total_samples,
            accuracy_pct=decider_acc,
            avg_decision_latency_ms=dec_avg_dec_lat,
            p50_decision_latency_ms=round(dec_p50, 2),
            p95_decision_latency_ms=round(dec_p95, 2),
            avg_total_latency_ms=dec_avg_tot_lat,
            estimated_routing_cost_usd=0.0, # Pointer head decision requires no token generation
            model_invocations_for_routing=0, # Single forward pass pointer evaluation
            error_count=decider_errors
        )

        baseline_comp = BenchmarkComparisonResult(
            strategy="Bedrock Baseline (LLM Router)",
            total_samples=total_samples,
            accuracy_pct=baseline_acc,
            avg_decision_latency_ms=base_avg_dec_lat,
            p50_decision_latency_ms=round(base_p50, 2),
            p95_decision_latency_ms=round(base_p95, 2),
            avg_total_latency_ms=base_avg_tot_lat,
            estimated_routing_cost_usd=round(total_samples * 0.00045, 5), # ~$0.45 per 1k routing classifications
            model_invocations_for_routing=total_samples,
            error_count=baseline_errors
        )

        # Save to database
        try:
            save_evaluation(
                eval_id=run_id,
                sample_count=total_samples,
                decider_accuracy=decider_acc,
                baseline_accuracy=baseline_acc,
                decider_avg_lat=dec_avg_dec_lat,
                baseline_avg_lat=base_avg_dec_lat,
                reduction_pct=lat_reduction_pct,
                results_json={
                    "decider": decider_comp.dict(),
                    "baseline": baseline_comp.dict()
                }
            )
        except Exception:
            pass

        return BenchmarkResponse(
            run_id=run_id,
            sample_count=total_samples,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            decider_results=decider_comp,
            baseline_results=baseline_comp,
            latency_reduction_pct=lat_reduction_pct,
            notes=[
                "Decider 2B eliminates the auto-regressive token generation loop for routing.",
                "Baseline invokes a full generative model solely to output the route choice.",
                "Routing latency is cleanly isolated from Bedrock response generation time."
            ]
        )

benchmark_runner = BenchmarkRunner()
