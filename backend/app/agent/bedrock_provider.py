import os
import json
import time
from typing import Optional, Dict, Any, Tuple
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
from app.config import settings
from app.schemas import ProcessingRoute

class BedrockModelProvider:
    """
    Amazon Bedrock Model Provider integrating with AWS SDK (boto3) and Strands Agent.
    Supports both real AWS Bedrock invocation and explicit, verifiable simulation demo mode.
    """

    def __init__(self):
        self.region = settings.aws_region
        self.client: Optional[Any] = None
        # Lazy initialization to prevent hanging on local metadata discovery
        if settings.app_mode == "live":
            self._init_client()

    def _init_client(self):
        try:
            self.client = boto3.client("bedrock-runtime", region_name=self.region)
        except Exception:
            self.client = None


    def is_available(self) -> Tuple[bool, str]:
        if not self.client:
            return False, "AWS credentials not detected in environment or AWS profile."
        return True, "AWS Bedrock client ready."

    def invoke(
        self,
        prompt: str,
        route: ProcessingRoute,
        is_demo: bool = False
    ) -> Tuple[str, str, float, bool]:
        """
        Invokes either the lightweight or advanced model on Bedrock.
        Returns (response_text, model_used, latency_ms, is_simulated).
        """
        model_id = (
            settings.bedrock_lightweight_model_id
            if route == ProcessingRoute.LIGHTWEIGHT
            else settings.bedrock_advanced_model_id
        )

        # Handle clarify route deterministically
        if route == ProcessingRoute.CLARIFY:
            clarify_text = (
                "Could you please provide more details or clarify your request? "
                "The current query does not contain sufficient context for safe execution."
            )
            return clarify_text, "deterministic-clarifier", 1.5, False

        # If in demo mode or AWS client not available
        if is_demo or not self.client:
            return self._simulate_bedrock_response(prompt, route, model_id)

        start_time = time.monotonic()
        try:
            # Bedrock Converse API or InvokeModel
            # Amazon Nova / Claude standard Converse format
            response = self.client.converse(
                modelId=model_id,
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                inferenceConfig={
                    "maxTokens": 1024,
                    "temperature": 0.2 if route == ProcessingRoute.LIGHTWEIGHT else 0.7
                }
            )
            latency_ms = (time.monotonic() - start_time) * 1000.0
            content = response["output"]["message"]["content"][0]["text"]
            return content, model_id, round(latency_ms, 2), False

        except (NoCredentialsError, ClientError, EndpointConnectionError) as e:
            # Explicit diagnostic error handling
            error_msg = f"[Bedrock Service Error: {str(e)}]. Falling back to local diagnostic simulation."
            sim_content, _, lat, _ = self._simulate_bedrock_response(prompt, route, model_id)
            return f"{error_msg}\n\n{sim_content}", model_id, round(lat, 2), True
        except Exception as e:
            return f"Error invoking Amazon Bedrock ({model_id}): {str(e)}", model_id, 0.0, True

    def _simulate_bedrock_response(
        self,
        prompt: str,
        route: ProcessingRoute,
        model_id: str
    ) -> Tuple[str, str, float, bool]:
        """
        Realistic, deterministic demo response generator.
        Explicitly marked with is_simulated=True.
        """
        time.sleep(0.08 if route == ProcessingRoute.LIGHTWEIGHT else 0.22)
        latency_ms = 85.0 if route == ProcessingRoute.LIGHTWEIGHT else 230.0

        p_lower = prompt.lower()
        if route == ProcessingRoute.LIGHTWEIGHT:
            if "capital of france" in p_lower:
                resp = "The capital of France is Paris."
            elif "good morning" in p_lower:
                resp = "Buenos días, ¿cómo estás?"
            elif "summarize" in p_lower:
                resp = "AI significantly transforms business operations."
            elif "spelling" in p_lower or "grammar" in p_lower:
                resp = "Corrected: 'They're going to their house now.'"
            elif "json" in p_lower:
                resp = '["apples", "bananas", "oranges"]'
            else:
                resp = f"[Amazon Bedrock Lightweight: {model_id}]\nDirect concise answer: Processed request with minimal inference overhead."
        else: # ADVANCED
            if "distributed event streaming" in p_lower or "architecture" in p_lower:
                resp = (
                    f"### Architecture Proposal ({model_id})\n\n"
                    "1. **Ingestion Layer:** Amazon Kinesis Data Streams / Amazon MSK across Primary (us-east-1) and Secondary (us-west-2) regions.\n"
                    "2. **Cross-Region Replication:** Active-Active mirror replication with Kafka MirrorMaker 2 or DynamoDB Global Tables for offset synchronization.\n"
                    "3. **Compute & Processing:** AWS Lambda and Amazon ECS tasks using event-driven idempotency keys to guarantee exactly-once semantic processing.\n"
                    "4. **Failover & Observability:** Amazon Route 53 Application Recovery Controller (ARC) with automated health probes and CloudWatch synthetic heartbeats."
                )
            elif "worker pool" in p_lower or "concurrency" in p_lower or "asyncio" in p_lower:
                resp = (
                    f"### Python Asyncio Leaky-Bucket Implementation ({model_id})\n\n"
                    "```python\n"
                    "import asyncio\n"
                    "import time\n\n"
                    "class LeakyBucketWorkerPool:\n"
                    "    def __init__(self, capacity: int, leak_rate_per_sec: float):\n"
                    "        self.capacity = capacity\n"
                    "        self.leak_rate = leak_rate_per_sec\n"
                    "        self.water = 0.0\n"
                    "        self.last_check = time.monotonic()\n"
                    "        self.lock = asyncio.Lock()\n\n"
                    "    async def acquire(self):\n"
                    "        async with self.lock:\n"
                    "            now = time.monotonic()\n"
                    "            elapsed = now - self.last_check\n"
                    "            self.water = max(0.0, self.water - elapsed * self.leak_rate)\n"
                    "            self.last_check = now\n"
                    "            if self.water + 1.0 <= self.capacity:\n"
                    "                self.water += 1.0\n"
                    "                return True\n"
                    "            await asyncio.sleep((self.water + 1.0 - self.capacity) / self.leak_rate)\n"
                    "            self.water = self.capacity\n"
                    "            return True\n"
                    "```"
                )
            else:
                resp = (
                    f"### Deep Analysis & Solution ({model_id})\n\n"
                    "Synthesized multi-step plan:\n"
                    "1. Decomposed requirements into modular dependencies.\n"
                    "2. Applied rigorous edge-case verification and risk mitigation.\n"
                    "3. Full multi-tier execution validated against architectural constraints."
                )

        return resp, model_id, latency_ms, True

bedrock_provider = BedrockModelProvider()
