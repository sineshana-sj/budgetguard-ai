# System Architecture Specification

## Overview
**BudgetGuard AI** couples **Strands Decider 2B** with **Amazon Bedrock** to solve the dual challenges of latency and excessive cost in agentic AI architectures.

## The Dual-System Architecture
BudgetGuard AI implements Daniel Kahneman's System 1 and System 2 cognitive processing paradigm:
- **System 1 (Strands Decider 2B):** Fast, automatic, low-latency pointer-head decision making. Used exclusively for categorizing incoming requests into discrete execution paths without generating tokens.
- **System 2 (Amazon Bedrock):** Deliberate, high-capacity generative reasoning through foundation models (Amazon Nova Pro / Claude 3.7 Sonnet).

```mermaid
graph TD
    Client[Client / SaaS Dashboard] -->|User Prompt| API[FastAPI Gateway]
    API --> Norm[Input Normalization & Safety Bounds]
    Norm --> Decider[Strands Decider 2B - System 1]
    
    Decider -->|LIGHTWEIGHT (~8ms)| LightBedrock[Amazon Bedrock: Nova Micro]
    Decider -->|ADVANCED (~8ms)| AdvBedrock[Amazon Bedrock: Nova Pro]
    Decider -->|CLARIFY (~8ms)| Clarify[Deterministic Guardrail]
    
    LightBedrock --> Persist[SQLite Audit Log & Latency Telemetry]
    AdvBedrock --> Persist
    Clarify --> Persist
    
    Persist --> Client
```

## Security & Reliability Design
1. **Zero Credential Exposure:** AWS credentials follow the IAM role and standard credential provider chain. No keys are ever passed to the frontend.
2. **Deterministic Clarification Paths:** Malformed, empty, or ambiguous queries are caught immediately by the `CLARIFY` choice, eliminating wasteful model executions.
3. **Calibrated Fallbacks:** If the Decider confidence score drops below `0.65`, the system conservatively escalates to `ADVANCED` or `CLARIFY` to guarantee safety.
