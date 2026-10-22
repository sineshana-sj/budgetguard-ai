import os
from typing import List
from pydantic import BaseModel, Field

class Settings(BaseModel):
    # App
    app_name: str = "BudgetGuard AI"
    environment: str = os.getenv("ENVIRONMENT", "development")
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "0.0.0.0")
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Mode: 'live' or 'demo'
    app_mode: str = os.getenv("APP_MODE", "demo")
    
    # AWS Bedrock
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_profile: str = os.getenv("AWS_PROFILE", "default")
    bedrock_lightweight_model_id: str = os.getenv(
        "BEDROCK_LIGHTWEIGHT_MODEL_ID", "amazon.nova-micro-v1:0"
    )
    bedrock_advanced_model_id: str = os.getenv(
        "BEDROCK_ADVANCED_MODEL_ID", "amazon.nova-pro-v1:0"
    )
    
    # Strands Decider
    decider_model_id: str = os.getenv(
        "DECIDER_MODEL_ID", "StrandsAgents/strands-decider-2B-hobson-v19"
    )
    decider_endpoint: str = os.getenv("DECIDER_ENDPOINT", "")
    decider_confidence_threshold: float = float(
        os.getenv("DECIDER_CONFIDENCE_THRESHOLD", "0.65")
    )
    
    # Storage
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./budgetguard.db")
    persist_raw_prompts: bool = os.getenv("PERSIST_RAW_PROMPTS", "false").lower() == "true"

settings = Settings()
