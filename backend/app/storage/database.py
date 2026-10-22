import sqlite3
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "budgetguard.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            request_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            prompt_preview TEXT NOT NULL,
            raw_prompt TEXT,
            route TEXT NOT NULL,
            confidence REAL,
            decision_latency_ms REAL NOT NULL,
            total_latency_ms REAL NOT NULL,
            model_used TEXT NOT NULL,
            reason TEXT NOT NULL,
            is_fallback INTEGER NOT NULL,
            is_demo INTEGER NOT NULL,
            status TEXT NOT NULL,
            metadata TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            eval_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            sample_count INTEGER NOT NULL,
            decider_accuracy REAL NOT NULL,
            baseline_accuracy REAL NOT NULL,
            decider_avg_latency_ms REAL NOT NULL,
            baseline_avg_latency_ms REAL NOT NULL,
            latency_reduction_pct REAL NOT NULL,
            results_json TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_request(
    request_id: str,
    prompt: str,
    route: str,
    confidence: Optional[float],
    decision_latency_ms: float,
    total_latency_ms: float,
    model_used: str,
    reason: str,
    is_fallback: bool,
    is_demo: bool,
    persist_raw: bool = False,
    metadata: Optional[Dict[str, Any]] = None
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    prompt_preview = prompt[:100] + ("..." if len(prompt) > 100 else "")
    raw_prompt_val = prompt if persist_raw else None
    
    cursor.execute("""
        INSERT INTO requests (
            request_id, timestamp, prompt_preview, raw_prompt, route,
            confidence, decision_latency_ms, total_latency_ms, model_used,
            reason, is_fallback, is_demo, status, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        request_id,
        datetime.utcnow().isoformat() + "Z",
        prompt_preview,
        raw_prompt_val,
        route,
        confidence,
        decision_latency_ms,
        total_latency_ms,
        model_used,
        reason,
        1 if is_fallback else 0,
        1 if is_demo else 0,
        "COMPLETED",
        json.dumps(metadata or {})
    ))
    conn.commit()
    conn.close()

def get_recent_history(limit: int = 50) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT request_id, timestamp, prompt_preview, route, model_used,
               confidence, decision_latency_ms, total_latency_ms, is_fallback, is_demo
        FROM requests
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "request_id": row["request_id"],
            "timestamp": row["timestamp"],
            "prompt_preview": row["prompt_preview"],
            "route": row["route"],
            "model_used": row["model_used"],
            "confidence": row["confidence"],
            "decision_latency_ms": row["decision_latency_ms"],
            "total_latency_ms": row["total_latency_ms"],
            "is_fallback": bool(row["is_fallback"]),
            "is_demo": bool(row["is_demo"]),
        }
        for row in rows
    ]

def get_analytics_summary() -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM requests")
    total = cursor.fetchone()["total"]
    
    if total == 0:
        conn.close()
        return {
            "total_requests": 0,
            "routes": {
                "lightweight_count": 0,
                "advanced_count": 0,
                "clarify_count": 0,
                "fallback_count": 0,
                "total_requests": 0,
            },
            "latency": {
                "p50_decision_ms": 0.0,
                "p95_decision_ms": 0.0,
                "avg_decision_ms": 0.0,
                "avg_total_ms": 0.0,
            },
            "estimated_savings_pct": 0.0,
            "accuracy_eval_pct": None,
        }
    
    cursor.execute("SELECT route, COUNT(*) as count FROM requests GROUP BY route")
    route_counts = {row["route"]: row["count"] for row in cursor.fetchall()}
    
    cursor.execute("SELECT COUNT(*) as fallback_count FROM requests WHERE is_fallback = 1")
    fallback_count = cursor.fetchone()["fallback_count"]
    
    cursor.execute("SELECT decision_latency_ms, total_latency_ms FROM requests ORDER BY decision_latency_ms ASC")
    latencies = cursor.fetchall()
    dec_lats = [r["decision_latency_ms"] for r in latencies]
    tot_lats = [r["total_latency_ms"] for r in latencies]
    
    avg_dec = sum(dec_lats) / len(dec_lats) if dec_lats else 0.0
    avg_tot = sum(tot_lats) / len(tot_lats) if tot_lats else 0.0
    
    p50_dec = dec_lats[int(len(dec_lats) * 0.50)] if dec_lats else 0.0
    p95_dec = dec_lats[int(len(dec_lats) * 0.95)] if dec_lats else 0.0
    
    light_cnt = route_counts.get("LIGHTWEIGHT", 0)
    adv_cnt = route_counts.get("ADVANCED", 0)
    clar_cnt = route_counts.get("CLARIFY", 0)
    
    # Calculate savings: requests routed to LIGHTWEIGHT consume ~80% less cost than ADVANCED
    # If all routed to ADVANCED: 1.0 cost per request.
    # With routing: (light_cnt * 0.2 + adv_cnt * 1.0) / total
    savings_pct = 0.0
    if total > 0 and (light_cnt + adv_cnt) > 0:
        base_cost = total * 1.0
        routed_cost = (light_cnt * 0.15) + (adv_cnt * 1.0) + (clar_cnt * 0.05)
        savings_pct = max(0.0, round(((base_cost - routed_cost) / base_cost) * 100.0, 1))
    
    cursor.execute("SELECT decider_accuracy FROM evaluations ORDER BY timestamp DESC LIMIT 1")
    eval_row = cursor.fetchone()
    accuracy_eval = eval_row["decider_accuracy"] if eval_row else None
    
    conn.close()
    
    return {
        "total_requests": total,
        "routes": {
            "lightweight_count": light_cnt,
            "advanced_count": adv_cnt,
            "clarify_count": clar_cnt,
            "fallback_count": fallback_count,
            "total_requests": total,
        },
        "latency": {
            "p50_decision_ms": round(p50_dec, 2),
            "p95_decision_ms": round(p95_dec, 2),
            "avg_decision_ms": round(avg_dec, 2),
            "avg_total_ms": round(avg_tot, 2),
        },
        "estimated_savings_pct": savings_pct,
        "accuracy_eval_pct": accuracy_eval,
    }

def save_evaluation(
    eval_id: str,
    sample_count: int,
    decider_accuracy: float,
    baseline_accuracy: float,
    decider_avg_lat: float,
    baseline_avg_lat: float,
    reduction_pct: float,
    results_json: Dict[str, Any]
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO evaluations (
            eval_id, timestamp, sample_count, decider_accuracy, baseline_accuracy,
            decider_avg_latency_ms, baseline_avg_latency_ms, latency_reduction_pct, results_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        eval_id,
        datetime.utcnow().isoformat() + "Z",
        sample_count,
        decider_accuracy,
        baseline_accuracy,
        decider_avg_lat,
        baseline_avg_lat,
        reduction_pct,
        json.dumps(results_json)
    ))
    conn.commit()
    conn.close()
