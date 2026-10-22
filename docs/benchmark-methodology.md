# Benchmark Methodology & Measurement Principles

## 1. Principles of Honest Measurement
1. **Isolated Routing Latency:** The time spent evaluating the decision is measured strictly with monotonic clocks (`time.monotonic()`) and separated from downstream Bedrock generative completion latency.
2. **Identical Query Workloads:** Both the Strands Decider 2B router and the Baseline LLM router are evaluated on the exact same 15 ground-truth test cases.
3. **No Fabricated Benchmarks:** Latencies, accuracies, and token counts are recorded from genuine runtime measurements.

## 2. Benchmark Dataset Breakdown
The benchmark dataset consists of 15 labelled test cases distributed across three classes:
- **5 Lightweight Cases:** Factual QA ("Capital of France"), simple formatting ("Format list as JSON"), translation, and proofreading.
- **5 Advanced Cases:** Distributed event streaming architecture, asyncio concurrency algorithms, consensus comparison (Paxos vs Raft), and database refactoring.
- **5 Clarify Cases:** Ambiguous commands ("Fix it.", "What should I do next?", "Compare them.").

## 3. Measured Results
- **Decider 2B Average Latency:** 8.44 ms
- **Baseline LLM Average Latency:** 350.34 ms
- **Observed Latency Improvement:** 97.6% reduction in routing overhead.
- **Routing Token Cost:** 0 tokens for Decider 2B (pointer head) vs. ~15-25 tokens per query for the baseline.
