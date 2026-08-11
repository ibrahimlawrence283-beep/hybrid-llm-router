"""
Meridian Telemetry & Governance Gateway -- FastAPI Gateway
Handles prompt routing (semantic cache -> ML complexity router -> downstream model).
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import time

from complexity_classifier import classify

app = FastAPI(
    title="Meridian Telemetry & Governance Gateway",
    description="Enterprise-grade Hybrid ML + LLM Router with cost & latency tracking.",
    version="1.1.0",
)


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, examples=["What is the capital of France?"])


class ChatResponse(BaseModel):
    prompt: str
    complexity: str
    selected_model: str
    confidence: float
    latency_ms: float


@app.get("/health")
def health():
    return {"status": "ok", "service": "Meridian Gateway"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    start_time = time.time()

    # 1. Classify prompt complexity using trained ML classifier
    route = classify(request.prompt)
    complexity = route["complexity"]
    confidence = route["confidence"]

    # 2. Select target LLM tier based on classification & confidence guardrail
    CONFIDENCE_THRESHOLD = 0.60
    if complexity == "heavy" or confidence < CONFIDENCE_THRESHOLD:
        selected_model = "gpt-4o"
    else:
        selected_model = "llama-3.1-8b"

    latency_ms = round((time.time() - start_time) * 1000, 2)

    return ChatResponse(
        prompt=request.prompt,
        complexity=complexity,
        selected_model=selected_model,
        confidence=round(confidence, 3),
        latency_ms=latency_ms,
    )