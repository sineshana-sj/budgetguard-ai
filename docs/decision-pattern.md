# Decision Pattern: Model Routing (#model-routing)

## 1. Intent
In multi-agent systems, general-purpose LLMs should not be invoked simply to decide which specialized model or tool to invoke. The `#model-routing` pattern provides a typed, calibrated classification step using a specialized 2B decision model prior to any generative invocation.

## 2. Typed Decision Contract
- **Question:** `"Which processing route is appropriate for this request?"`
- **Type:** `choice`
- **Supported Choices:**
  - `LIGHTWEIGHT`: Direct factual queries, grammar corrections, translations, or simple list transformations.
  - `ADVANCED`: Deep architectural designs, multi-threaded coding, complex reasoning, or multi-step logic.
  - `CLARIFY`: Ambiguous, under-specified requests lacking essential context.

## 3. Confidence Threshold Gating
- Default Threshold: `0.65`
- Behavior on Low Confidence: If `confidence < 0.65` on a `LIGHTWEIGHT` prediction, the query is conservatively routed to `ADVANCED` to ensure user satisfaction is never degraded by underpowered execution.
