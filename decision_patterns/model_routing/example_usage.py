import sys
import os

# Standalone execution support
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from decision_patterns.model_routing.routing_handler import ModelRoutingHandler
from decision_patterns.model_routing.typed_question import ProcessingRoute

def main():
    router = ModelRoutingHandler(confidence_threshold=0.70)
    
    samples = [
        "What is the capital of France?",
        "Design a distributed event streaming architecture on AWS with multi-region active-active failover.",
        "Fix it."
    ]
    
    print("=== Strands Decider 2B: Model Routing Decision Recipe Demo ===")
    for prompt in samples:
        result = router.decide_route(prompt)
        print(f"\nPrompt: '{prompt}'")
        print(f"  -> Route: {result.route.value}")
        print(f"  -> Confidence: {result.confidence}")
        print(f"  -> Decision Latency: {result.decision_latency_ms} ms")
        print(f"  -> Is Fallback: {result.is_fallback}")

if __name__ == "__main__":
    main()
