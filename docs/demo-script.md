# BudgetGuard AI — Demonstration Video Script (< 3 Minutes)

**Total Duration:** 2 minutes 45 seconds

---

### [0:00 - 0:25] Introduction & The Problem
**Visual:** Opening view of the BudgetGuard AI dashboard (Overview tab).
**Audio/Voiceover:**
> "Welcome to BudgetGuard AI, built for the Strands Decider Hackathon.
> When building agentic applications, one of the biggest hidden costs is model routing. Developers frequently call large, expensive language models just to decide which model or tool to invoke next. That wastes 400 to 800 milliseconds and piles on token costs before real work even begins.
> BudgetGuard AI solves this using Strands Decider 2B paired with Amazon Bedrock."

---

### [0:25 - 0:55] Lightweight Routing Flow
**Visual:** Switch to **Live Playground**. Click the preset *Simple Query (Lightweight)*: *"What is the capital of France?"* and click **Submit Request**.
**Audio/Voiceover:**
> "Let's submit a simple factual query. In under 9 milliseconds, Strands Decider 2B categorizes this as a LIGHTWEIGHT request with 92% confidence.
> Instead of calling an expensive reasoning model, the agent directs it to Amazon Nova Micro. The user receives a fast, concise answer, saving up to 85% in inference costs."

---

### [0:55 - 1:25] Advanced Systems Architecture Flow
**Visual:** Click *System Architecture (Advanced)*: *"Design a high-throughput distributed event streaming architecture on AWS with active-active failover."* and click **Submit Request**.
**Audio/Voiceover:**
> "Now let's submit a complex architectural engineering request.
> Decider 2B immediately identifies the deep reasoning requirement and assigns the ADVANCED route with 95% confidence.
> The request is handed to Amazon Nova Pro, which generates a comprehensive multi-tier architecture with Kinesis, Lambda, and Route 53 failover."

---

### [1:25 - 1:50] Ambiguous Input & Clarification Guardrail
**Visual:** Click *Ambiguous Request (Clarify)*: *"Fix it."* and click **Submit Request**.
**Audio/Voiceover:**
> "What happens with ambiguous inputs like 'Fix it.'?
> Traditional agents often burn tokens guessing what the user meant. Decider 2B detects the lack of context and triggers the CLARIFY route.
> Our deterministic guard immediately prompts the user for clarification—costing zero LLM tokens and zero inference delay."

---

### [1:50 - 2:20] Decision Inspector & Reusable Pattern
**Visual:** Navigate to the **Decision Inspector** tab.
**Audio/Voiceover:**
> "In the Decision Inspector, we can see the exact typed question contract: 'Which processing route is appropriate for this request?' with discrete choices.
> Because Decider 2B uses a pointer head instead of generating token sequences, routing happens in a single parallel pass.
> We've packaged this complete pattern into a standalone, reusable decision recipe that any developer can drop into their agentic workflow."

---

### [2:20 - 2:45] Benchmark Lab & Conclusion
**Visual:** Navigate to the **Benchmark Lab** tab and click **Run Live Benchmark**.
**Audio/Voiceover:**
> "Finally, let's run the Benchmark Lab across 15 ground-truth test cases.
> The results speak for themselves: Strands Decider 2B averages 8.4 milliseconds for routing decisions, compared to 350 milliseconds for the Bedrock LLM routing baseline—a 97.6% latency reduction.
> BudgetGuard AI: Smarter AI decisions. Lower inference costs. Faster responses. Thank you!"
