import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from decision_patterns.model_routing.routing_handler import ModelRoutingHandler
from decision_patterns.model_routing.typed_question import ProcessingRoute

def test_reusable_recipe_cases():
    test_file = os.path.join(os.path.dirname(__file__), "..", "test_cases.json")
    with open(test_file, "r") as f:
        cases = json.load(f)
    
    handler = ModelRoutingHandler()
    for case in cases:
        res = handler.decide_route(case["prompt"])
        assert res.route.value == case["expected_route"], f"Failed for {case['prompt']}"
        assert res.confidence is not None
        assert res.decision_latency_ms > 0
