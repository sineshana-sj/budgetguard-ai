# Reusable Decision Recipe: Model Routing (#model-routing)

This recipe provides a drop-in pattern using **Strands Decider 2B** to perform low-latency typed model routing in agentic AI workflows.

## Pattern Overview
Instead of invoking a slow, expensive generative model to determine whether a query is simple or complex, **Strands Decider 2B** evaluates the request state in a single parallel forward pass through a pointer head.

- **Question:** "Which processing route is appropriate for this request?"
- **Choices:** `LIGHTWEIGHT`, `ADVANCED`, `CLARIFY`
- **Latency:** ~8-15 ms (vs. 350-800 ms with generative LLMs)
- **Cost:** Zero token-generation overhead for the decision itself.

## Contents
1. `typed_question.py`: The Pydantic model contract for the typed question, choices, and routing criteria.
2. `routing_handler.py`: The `ModelRoutingHandler` integrating with Strands SDK `InterventionHandler`.
3. `example_usage.py`: Minimal standalone executable script demonstrating routing.
4. `test_cases.json`: Ground-truth test cases across all routes.
5. `tests/`: Automated unit tests for recipe verification.

## Quickstart
```bash
python example_usage.py
```

## How to Reuse in Your Project
```python
from decision_patterns.model_routing.routing_handler import ModelRoutingHandler
from decision_patterns.model_routing.typed_question import ProcessingRoute

router = ModelRoutingHandler(confidence_threshold=0.65)
result = router.decide_route("What is the capital of France?")

if result.route == ProcessingRoute.LIGHTWEIGHT:
    # Route to fast model (e.g. Amazon Nova Micro / Claude 3 Haiku)
    ...
elif result.route == ProcessingRoute.ADVANCED:
    # Route to reasoning model (e.g. Amazon Nova Pro / Claude 3.7 Sonnet)
    ...
elif result.route == ProcessingRoute.CLARIFY:
    # Return clarification prompt without invoking LLM
    ...
```
