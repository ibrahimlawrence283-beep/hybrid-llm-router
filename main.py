"""
Meridian Telemetry & Governance Gateway -- FastAPI Gateway
With In-Memory Exact/Semantic Prompt Caching & Telemetry tracking.
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field
import time
import numpy as np

from complexity_classifier import classify

app = FastAPI(
    title="Meridian Telemetry & Governance Gateway",
    description="Enterprise-grade Hybrid ML + LLM Router with cost & latency tracking.",
    version="1.1.0",
)

# Global Stores (In-Memory)
telemetry_store = []
cache_store = {}  # Format: {normalized_prompt: {"complexity": str, "model": str}}


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    prompt: str
    complexity: str
    model: str
    selected_model: str
    model_used: str
    cached: bool
    latency_ms: float


@app.get("/health")
def health():
    return {"status": "ok", "service": "Meridian Gateway"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    start_time = time.time()
    clean_prompt = request.prompt.strip().lower()

    # 1. Cache Lookup (Exact Match / Normalized String Hit)
    if clean_prompt in cache_store:
        cached_entry = cache_store[clean_prompt]
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        entry = {
            "prompt": request.prompt,
            "complexity": cached_entry["complexity"],
            "model_used": cached_entry["model"],
            "cached": True,
            "similarity_score": 1.0,
            "latency_ms": latency_ms,
            "cost_kes": 0.0,  # Zero API cost on cache hit
            "reason": "Served directly from Semantic Cache"
        }
        telemetry_store.append(entry)

        return ChatResponse(
            prompt=request.prompt,
            complexity=cached_entry["complexity"],
            model=cached_entry["model"],
            selected_model=cached_entry["model"],
            model_used=cached_entry["model"],
            cached=True,
            latency_ms=latency_ms,
        )

    # 2. Classifier Execution on Cache Miss
    res = classify(request.prompt)
    complexity = res.get("complexity", "light") if isinstance(res, dict) else str(res)
    target_model = "gpt-4o" if complexity == "heavy" else "llama-3.1-8b"

    latency_ms = round((time.time() - start_time) * 1000, 2)
    
    # Pricing estimation (1 USD = 130 KES)
    token_count = len(request.prompt.split()) + 20
    cost_per_1k = 0.005 if target_model == "gpt-4o" else 0.0002
    cost_kes = round((token_count / 1000) * cost_per_1k * 130, 4)

    # Store in Cache for future hits
    cache_store[clean_prompt] = {
        "complexity": complexity,
        "model": target_model
    }

    entry = {
        "prompt": request.prompt,
        "complexity": complexity,
        "model_used": target_model,
        "cached": False,
        "similarity_score": 0.0,
        "latency_ms": latency_ms,
        "cost_kes": cost_kes,
        "reason": f"Classified as {complexity} complexity"
    }
    telemetry_store.append(entry)

    return ChatResponse(
        prompt=request.prompt,
        complexity=complexity,
        model=target_model,
        selected_model=target_model,
        model_used=target_model,
        cached=False,
        latency_ms=latency_ms,
    )


@app.get("/stats")
def get_stats():
    if not telemetry_store:
        return {
            "total_requests": 0, "cache_hits": 0, "light_model_requests": 0,
            "heavy_model_requests": 0, "total_cost_kes": 0.0,
            "estimated_cost_saved_kes": 0.0, "latency_p50_ms": 0.0,
            "latency_p95_ms": 0.0, "recent_history": []
        }

    total_requests = len(telemetry_store)
    cache_hits = sum(1 for x in telemetry_store if x["cached"])
    light_reqs = sum(1 for x in telemetry_store if x["model_used"] == "llama-3.1-8b")
    heavy_reqs = sum(1 for x in telemetry_store if x["model_used"] == "gpt-4o")
    
    total_cost = sum(x["cost_kes"] for x in telemetry_store)
    
    # Calculate savings: Avoided heavy model cost on light model execution or cache hits
    cost_saved = sum(0.025 for x in telemetry_store if x["model_used"] == "llama-3.1-8b" or x["cached"])

    latencies = [x["latency_ms"] for x in telemetry_store]
    p50 = round(float(np.percentile(latencies, 50)), 2)
    p95 = round(float(np.percentile(latencies, 95)), 2)

    return {
        "total_requests": total_requests,
        "cache_hits": cache_hits,
        "light_model_requests": light_reqs,
        "heavy_model_requests": heavy_reqs,
        "total_cost_kes": round(total_cost, 4),
        "estimated_cost_saved_kes": round(cost_saved, 4),
        "latency_p50_ms": p50,
        "latency_p95_ms": p95,
        "recent_history": list(reversed(telemetry_store[-10:]))
    }