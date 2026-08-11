"""
Enterprise RAG w/ RBAC & ML Router -- retrieval API.

Retrieval-only by default: no GPU or LLM API key required, so this runs
in any container including free-tier Codespaces. See generation.py for
how to plug in an LLM to add answer synthesis on top of retrieval.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.data_loader import KnowledgeBase
from app.retrieval import hybrid_search
from app.rbac import get_allowed_roles, UnknownRoleError
from complexity_classifier import classify

GENERATION_ENABLED = False  # flip on once generation.py has a real provider wired in

app = FastAPI(
    title="Enterprise RAG w/ RBAC & ML Router",
    description=(
        "RBAC-filtered hybrid retrieval (vector + BM25 + RRF) over a "
        "multi-department enterprise knowledge base with integrated ML-driven "
        "query complexity classification for optimal model routing. Access is enforced "
        "at the retrieval layer -- a role can never retrieve a document "
        "outside its permitted departments/sensitivity tiers."
    ),
    version="1.1.0",
)

kb: KnowledgeBase | None = None


@app.on_event("startup")
def load_knowledge_base():
    global kb
    kb = KnowledgeBase()


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, examples=["What is the remote work policy?"])
    role: str = Field(..., examples=["employee"])
    top_k: int = Field(5, ge=1, le=20)


class RetrievedDoc(BaseModel):
    doc_id: str
    department: str
    sensitivity: str
    content: str
    score: float


class QueryResponse(BaseModel):
    question: str
    role: str
    complexity: str
    selected_model: str
    confidence: float
    results: list[RetrievedDoc]


@app.get("/health")
def health():
    return {"status": "ok", "documents_loaded": kb.doc_count() if kb else 0}


@app.get("/roles")
def roles():
    return {"available_roles": get_allowed_roles()}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    if kb is None:
        raise HTTPException(status_code=503, detail="Knowledge base not loaded yet")

    # 1. Classify prompt complexity using trained ML classifier
    route = classify(request.question)
    complexity = route["complexity"]
    confidence = route["confidence"]

    # 2. Select target LLM tier based on classification & confidence guardrail
    CONFIDENCE_THRESHOLD = 0.60
    if complexity == "heavy" or confidence < CONFIDENCE_THRESHOLD:
        selected_model = "gpt-4o"
    else:
        selected_model = "llama-3.1-8b"

    # 3. Perform RBAC-enforced hybrid retrieval
    try:
        results = hybrid_search(kb, request.question, request.role, top_k=request.top_k)
    except UnknownRoleError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return QueryResponse(
        question=request.question,
        role=request.role,
        complexity=complexity,
        selected_model=selected_model,
        confidence=round(confidence, 3),
        results=results,
    )