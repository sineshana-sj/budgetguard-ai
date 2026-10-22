from typing import List, Dict, Any
from app.schemas import ProcessingRoute

BENCHMARK_DATASET: List[Dict[str, Any]] = [
    # Lightweight requests
    {
        "id": "lw-01",
        "prompt": "What is the capital of France?",
        "expected_route": ProcessingRoute.LIGHTWEIGHT,
        "description": "Factual direct question"
    },
    {
        "id": "lw-02",
        "prompt": "Summarize this sentence in 5 words: 'Artificial intelligence is transforming business processes.'",
        "expected_route": ProcessingRoute.LIGHTWEIGHT,
        "description": "Simple sentence summarization"
    },
    {
        "id": "lw-03",
        "prompt": "Translate 'Good morning, how are you?' to Spanish.",
        "expected_route": ProcessingRoute.LIGHTWEIGHT,
        "description": "Standard translation"
    },
    {
        "id": "lw-04",
        "prompt": "Check spelling and grammar: 'Their going to there house now.'",
        "expected_route": ProcessingRoute.LIGHTWEIGHT,
        "description": "Proofreading"
    },
    {
        "id": "lw-05",
        "prompt": "Format this list as JSON: apples, bananas, oranges.",
        "expected_route": ProcessingRoute.LIGHTWEIGHT,
        "description": "Trivial data formatting"
    },
    
    # Advanced requests
    {
        "id": "adv-01",
        "prompt": "Design a high-throughput distributed event streaming architecture on AWS with multi-region active-active failover and zero data loss.",
        "expected_route": ProcessingRoute.ADVANCED,
        "description": "Complex systems architecture"
    },
    {
        "id": "adv-02",
        "prompt": "Write a Python concurrent worker pool implementing leaky-bucket rate limiting with asyncio and redis distributed locks.",
        "expected_route": ProcessingRoute.ADVANCED,
        "description": "Advanced concurrency and algorithms"
    },
    {
        "id": "adv-03",
        "prompt": "Analyze the trade-offs between Paxos and Raft consensus algorithms regarding leader election overhead and network partition recovery.",
        "expected_route": ProcessingRoute.ADVANCED,
        "description": "Deep computer science analysis"
    },
    {
        "id": "adv-04",
        "prompt": "Draft a multi-step migration strategy moving a legacy 50-table monolithic relational database to event-sourced microservices.",
        "expected_route": ProcessingRoute.ADVANCED,
        "description": "Multi-step complex refactoring"
    },
    {
        "id": "adv-05",
        "prompt": "Prove why Dijkstra's algorithm fails with negative edge weights and formulate the Bellman-Ford recurrence relation.",
        "expected_route": ProcessingRoute.ADVANCED,
        "description": "Mathematical algorithm proof"
    },

    # Clarification requests
    {
        "id": "clr-01",
        "prompt": "Fix it.",
        "expected_route": ProcessingRoute.CLARIFY,
        "description": "Zero context ambiguous request"
    },
    {
        "id": "clr-02",
        "prompt": "What should I do next?",
        "expected_route": ProcessingRoute.CLARIFY,
        "description": "Under-specified decision query"
    },
    {
        "id": "clr-03",
        "prompt": "Send the update to everyone.",
        "expected_route": ProcessingRoute.CLARIFY,
        "description": "Ambiguous recipient and content"
    },
    {
        "id": "clr-04",
        "prompt": "Run the script.",
        "expected_route": ProcessingRoute.CLARIFY,
        "description": "Missing file or action details"
    },
    {
        "id": "clr-05",
        "prompt": "Compare them.",
        "expected_route": ProcessingRoute.CLARIFY,
        "description": "Missing entities to compare"
    }
]
