from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.schemas import (
    ChatRequest, ChatResponse, AnalyticsResponse, HistoryItem, BenchmarkResponse
)
from app.agent.orchestrator import orchestrator
from app.storage.database import get_recent_history, get_analytics_summary
from app.evaluation.benchmark import benchmark_runner
from app.agent.bedrock_provider import bedrock_provider
from app.agent.decider_adapter import decider_adapter
from app.config import settings

router = APIRouter()

@router.get("/health")
def health_check():
    bedrock_ok, bedrock_msg = bedrock_provider.is_available()
    decider_ok, decider_msg = decider_adapter.is_available()
    
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "mode": settings.app_mode,
        "components": {
            "strands_decider_2b": {
                "available": decider_ok,
                "detail": decider_msg,
                "model_id": settings.decider_model_id,
                "threshold": settings.decider_confidence_threshold
            },
            "amazon_bedrock": {
                "available": bedrock_ok,
                "detail": bedrock_msg,
                "region": settings.aws_region,
                "lightweight_model": settings.bedrock_lightweight_model_id,
                "advanced_model": settings.bedrock_advanced_model_id
            }
        }
    }

@router.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        return orchestrator.process_request(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Request processing failed: {str(e)}")

@router.get("/api/analytics", response_model=AnalyticsResponse)
def analytics_endpoint():
    try:
        data = get_analytics_summary()
        bedrock_ok, bedrock_msg = bedrock_provider.is_available()
        decider_ok, decider_msg = decider_adapter.is_available()
        
        data["system_status"] = {
            "mode": settings.app_mode,
            "bedrock_ready": bedrock_ok,
            "decider_ready": decider_ok,
            "aws_region": settings.aws_region
        }
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed retrieving analytics: {str(e)}")

@router.get("/api/history", response_model=List[HistoryItem])
def history_endpoint(limit: int = Query(50, ge=1, le=200)):
    try:
        return get_recent_history(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed retrieving history: {str(e)}")

@router.post("/api/evaluate", response_model=BenchmarkResponse)
def evaluate_endpoint(sample_limit: int = Query(15, ge=3, le=50)):
    try:
        return benchmark_runner.run_benchmark(sample_limit=sample_limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark execution failed: {str(e)}")
