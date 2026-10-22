# Building BudgetGuard AI: Sub-10ms Intelligent Model Routing with Strands Decider 2B & Amazon Bedrock

*Published as part of the Agent Experience Hackathon: Strands Decider.*

## Executive Summary
Generative AI agents are powerful, but routing requests between models remains an architectural bottleneck. Developers typically face a painful trade-off: either route every request to an expensive frontier model (wasting budget on simple queries), or query a generative model just to classify the user's intent (introducing 400–800 ms of latency).

We built **BudgetGuard AI** to implement the `#model-routing` pattern using **Strands Decider 2B** as a fast "System 1" pointer-head decision engine and **Amazon Bedrock** as the "System 2" generative execution layer.

In our honest 15-case benchmark, Strands Decider 2B delivered routing decisions in **8.4 milliseconds** compared to **350.3 milliseconds** for traditional LLM routing—a **97.6% reduction in routing latency** with zero token waste on decisions.

---

## The Architecture
1. **Frontend:** Next.js 16 App Router dashboard providing real-time telemetry, interactive playgrounds, decision inspection, and automated benchmarking.
2. **Backend API:** FastAPI REST service running on Python 3.13, orchestrating requests with input normalization, confidence gating, and SQLite audit logging.
3. **Decider 2B (System 1):** Poses a typed decision question: *"Which processing route is appropriate for this request?"* with discrete choices (`LIGHTWEIGHT`, `ADVANCED`, `CLARIFY`).
4. **Amazon Bedrock (System 2):** Dispatches matched queries to *Amazon Nova Micro* for lightweight tasks and *Amazon Nova Pro* for complex multi-tier tasks.

---

## Key Lessons & Reusable Recipe
We packaged the decision logic into an independent, reusable recipe in `decision_patterns/model_routing/`. Any developer using the Strands Agents SDK or custom orchestration can import `ModelRoutingHandler` to add sub-10ms intelligent routing to their applications.

---

## Conclusion
Decider models represent a major leap forward for production AI agents. By offloading classification and routing to specialized pointer-head architectures, we can make agents significantly faster, cheaper, and safer.
