import sys
import os

sys.path = [p for p in sys.path if not p.lower().rstrip('\\/').endswith('desktop')]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


try:
    from app.main import app
    print("STATUS: APP IMPORT SUCCESSFUL")
    
    from app.agent.orchestrator import orchestrator
    from app.schemas import ChatRequest
    
    res1 = orchestrator.process_request(ChatRequest(prompt="What is the capital of France?"))
    print(f"TEST 1 (LIGHTWEIGHT): Route={res1.route.value}, Model={res1.model_used}, Latency={res1.decision.decision_latency_ms}ms")
    
    res2 = orchestrator.process_request(ChatRequest(prompt="Design a distributed event streaming architecture on AWS with active-active failover"))
    print(f"TEST 2 (ADVANCED): Route={res2.route.value}, Model={res2.model_used}, Latency={res2.decision.decision_latency_ms}ms")
    
    res3 = orchestrator.process_request(ChatRequest(prompt="Fix it."))
    print(f"TEST 3 (CLARIFY): Route={res3.route.value}, Model={res3.model_used}, Latency={res3.decision.decision_latency_ms}ms")

    from app.evaluation.benchmark import benchmark_runner
    bench = benchmark_runner.run_benchmark(sample_limit=3)
    print(f"TEST 4 (BENCHMARK): Samples={bench.sample_count}, Decider Latency={bench.decider_results.avg_decision_latency_ms}ms, Baseline Latency={bench.baseline_results.avg_decision_latency_ms}ms, Latency Reduction={bench.latency_reduction_pct}%")

    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY")
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
