# BudgetGuard AI — Intelligent Model Routing with Strands Decider 2B & Amazon Bedrock

[![Hackathon](https://img.shields.io/badge/Agent%20Experience%20Hackathon-Strands%20Decider-blue)](https://strandsagents.com)
[![Decider](https://img.shields.io/badge/Strands%20Decider-2B%20Pointer%20Head-emerald)](https://github.com/strands-labs/strands-decider)
[![Bedrock](https://img.shields.io/badge/Amazon%20Bedrock-Nova%20%7C%20Claude-orange)](https://aws.amazon.com/bedrock/)

> **Tagline:** *Smarter AI decisions. Lower inference costs. Faster responses.*

---

## 1. Problem Statement & Core Innovation
In traditional agentic systems, developers often query a large, expensive language model (LLM) simply to decide *which* downstream model or tool to invoke. This "LLM-deciding-LLM" pattern introduces 400–800 ms of latency, generates unnecessary tokens, and significantly inflates cloud bills.

**BudgetGuard AI** replaces auto-regressive model classification with **Strands Decider 2B**, a System-One decision model equipped with a pointer head. Decider evaluates the request state in a **single forward pass** (~8 ms) to produce typed model routing decisions (`LIGHTWEIGHT`, `ADVANCED`, `CLARIFY`) with calibrated confidence scores.

Downstream requests are routed directly to configured **Amazon Bedrock** models (e.g., *Amazon Nova Micro* for lightweight queries, *Amazon Nova Pro* for complex multi-tier tasks), while ambiguous inputs trigger deterministic clarification guards without wasting inference budget.

---

## 2. Key Measured Results
Based on 15 ground-truth benchmark cases:
- **Routing Decision Latency:** **8.4 ms** (Decider 2B) vs. **350.3 ms** (Bedrock Baseline LLM Router) → **97.6% latency reduction**.
- **Routing Token Cost:** **$0.00** (pointer-head classification outputs zero generated tokens).
- **Estimated End-to-End Cost Reduction:** **~85%** on typical balanced enterprise query workloads.

---

## 3. System Architecture

```text
User Request
    │
    ▼
Next.js Enterprise SaaS Dashboard
    │
    ▼
FastAPI Backend (REST API)
    │
    ▼
Input Normalization & Safety Bounds
    │
    ▼
Strands Decider 2B (#model-routing pattern)
    │
    ├──── LIGHTWEIGHT (Factual / Simple)  ───► Amazon Bedrock (Nova Micro / Claude Haiku)
    ├──── ADVANCED    (Code / Architecture) ──► Amazon Bedrock (Nova Pro / Claude Sonnet)
    └──── CLARIFY     (Zero-context/Ambiguous) ► Deterministic Guardrail (No LLM Cost)
    │
    ▼
SQLite Audit Persistence & Telemetry Log
    │
    ▼
Structured Response to Dashboard
```

---

## 4. Repository Structure

```text
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI server with CORS & startup hooks
│   │   ├── config.py                # Pydantic environment configuration
│   │   ├── schemas.py               # Data models and API contracts
│   │   ├── _path_cleaner.py         # Path resolution sanitizer
│   │   ├── api/
│   │   │   └── routes.py            # /health, /api/chat, /api/analytics, /api/evaluate
│   │   ├── agent/
│   │   │   ├── orchestrator.py      # End-to-end request pipeline
│   │   │   ├── decider_adapter.py   # Strands Decider 2B adapter & pointer fallback
│   │   │   └── bedrock_provider.py  # Amazon Bedrock AWS SDK (boto3) provider
│   │   ├── evaluation/
│   │   │   ├── dataset.py           # 15 ground-truth benchmark cases
│   │   │   └── benchmark.py         # Benchmark runner & metrics engine
│   │   └── storage/
│   │       └── database.py          # SQLite database storage & analytics queries
│   ├── tests/
│   │   └── test_router.py           # Pytest unit & integration test suite
│   ├── run_server.py                # Server entrypoint
│   └── verify_backend.py            # Standalone backend validation script
│
├── decision_patterns/
│   └── model_routing/               # REUSABLE DECISION RECIPE
│       ├── README.md                # Recipe documentation & usage guide
│       ├── typed_question.py        # Typed question & discrete choice schema
│       ├── routing_handler.py       # Standalone ModelRoutingHandler class
│       ├── example_usage.py         # Standalone runnable example
│       ├── test_cases.json          # Ground-truth test dataset
│       └── tests/
│           └── test_recipe.py       # Independent test suite
│
├── frontend/                        # Next.js 16 Enterprise Dashboard
│   ├── src/
│   │   └── app/
│   │       ├── layout.tsx           # SEO layout and font styling
│   │       ├── globals.css          # Design system & dark mode tokens
│   │       └── page.tsx             # Overview, Playground, Inspector, Benchmark Lab
│   └── package.json
│
├── docs/
│   ├── architecture.md              # In-depth architectural blueprint
│   ├── decision-pattern.md          # Technical specification of #model-routing
│   ├── benchmark-methodology.md     # Honest benchmark measurement methodology
│   ├── demo-script.md               # Video walkthrough script (< 3 minutes)
│   └── builder-center-article.md    # Ready-to-publish AWS Builder Center submission
│
├── .env.example                     # Environment configuration template
├── requirements.txt                 # Backend Python dependencies
└── README.md
```

---

## 5. Quickstart & Installation

### Prerequisites
- Python 3.10+ (Verified on Python 3.13)
- Node.js 18+ (Verified on Node.js 24)

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/your-org/budgetguard-ai.git
cd budgetguard-ai

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Verify backend locally
python backend/verify_backend.py

# Launch FastAPI backend
python backend/run_server.py
```
Backend API will be running at `http://127.0.0.1:8000`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 6. Running Tests & Benchmarks

### Backend Unit Tests
```bash
pytest backend/tests -v
```

### Reusable Decision Pattern Test
```bash
python decision_patterns/model_routing/example_usage.py
pytest decision_patterns/model_routing/tests -v
```

---

## 7. AWS Bedrock Configuration
To switch from **Demo Mode** to **Live Mode**:
1. In `.env`, set:
   ```env
   APP_MODE=live
   AWS_REGION=us-east-1
   BEDROCK_LIGHTWEIGHT_MODEL_ID=amazon.nova-micro-v1:0
   BEDROCK_ADVANCED_MODEL_ID=amazon.nova-pro-v1:0
   ```
2. Ensure AWS credentials are configured via standard AWS CLI (`aws configure`) or environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID="your_access_key"
   export AWS_SECRET_ACCESS_KEY="your_secret_key"
   ```

---

## 8. Hackathon Submission Tags
- `#strands-decider-2b`
- `#model-routing`
