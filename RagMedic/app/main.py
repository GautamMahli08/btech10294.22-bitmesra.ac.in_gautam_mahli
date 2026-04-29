from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
from app.ingestion.auto_ingestor import auto_ingest_for_query
from app.rag.confidence import calculate_confidence
from app.rag.retriever import retrieve_context
from app.rag.generator import generate_answer
from app.rag.qdrant_store import create_collection_if_not_exists
from app.rag.gate import is_good_enough
from app.ingestion.website_ingestor import (
    ingest_pubmed_query,
    ingest_cdc_page,
    ingest_who_page,
    ingest_nice_page,
)

from app.database import Base, engine, get_db
from app.models import QueryLog, User
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)


app = FastAPI(
    title="RagMedic API",
    description="Source-backed medical RAG assistant",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    create_collection_if_not_exists()
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "RagMedic backend running"}


def require_admin(user: User):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


# ---------------- AUTH ----------------

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == request.email).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=request.name,
        email=request.email,
        password_hash=hash_password(request.password),
        role="doctor",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
    })

    return {
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }


@app.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
    })

    return {
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }


@app.get("/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
    }


# ---------------- INGESTION ----------------

class IngestPubMedRequest(BaseModel):
    query: str
    limit: int = 5


class IngestUrlRequest(BaseModel):
    url: str


@app.post("/ingest/pubmed")
def ingest_pubmed(
    request: IngestPubMedRequest,
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    return ingest_pubmed_query(request.query, request.limit)


@app.post("/ingest/cdc-url")
def ingest_cdc_url_endpoint(
    request: IngestUrlRequest,
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    return ingest_cdc_page(request.url)


@app.post("/ingest/who-url")
def ingest_who_url_endpoint(
    request: IngestUrlRequest,
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    return ingest_who_page(request.url)


@app.post("/ingest/nice-url")
def ingest_nice_url_endpoint(
    request: IngestUrlRequest,
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)
    return ingest_nice_page(request.url)


# ---------------- ASK / RAG ----------------

class AskRequest(BaseModel):
    question: str


@app.post("/ask")
def ask_question(
    request: AskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    auto_ingestion_result = None
    q = request.question.lower()

    context, sources = retrieve_context(request.question)
    confidence_result = calculate_confidence(sources)

    needs_auto_ingest = not is_good_enough(sources, request.question)

    # Force auto-ingestion for known numeric/drug-dose questions
    if "metformin" in q and any(word in q for word in ["dose", "dosage", "starting", "start"]):
        needs_auto_ingest = True

    if "hba1c" in q and "target" in q:
        needs_auto_ingest = True

    if needs_auto_ingest:
        auto_ingestion_result = auto_ingest_for_query(request.question)

        context, sources = retrieve_context(request.question)
        confidence_result = calculate_confidence(sources)

    if not is_good_enough(sources, request.question):
        answer = "I could not find sufficient reliable medical evidence."
        confidence_result = {
            "confidence": "Low",
            "reason": "No relevant trusted medical sources were found.",
        }
    else:
        answer = generate_answer(context, request.question)

    log = QueryLog(
        question=request.question,
        answer=answer,
        confidence=confidence_result["confidence"],
        reason=confidence_result["reason"],
        sources=json.dumps(sources),
    )

    db.add(log)
    db.commit()

    return {
        "answer": answer,
        "confidence": confidence_result["confidence"],
        "reason": confidence_result["reason"],
        "sources": sources,
        "auto_ingestion": auto_ingestion_result,
    }


# ---------------- HISTORY ----------------

@app.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    logs = (
        db.query(QueryLog)
        .order_by(QueryLog.created_at.desc())
        .limit(50)
        .all()
    )

    result = []

    for log in logs:
        sources = []

        if log.sources:
            try:
                raw_sources = json.loads(log.sources)

                for s in raw_sources:
                    sources.append({
                        "title": s.get("title"),
                        "url": s.get("url"),
                        "source": s.get("source"),
                        "score": s.get("score"),
                    })
            except:
                sources = []

        result.append({
            "id": log.id,
            "question": log.question,
            "answer": log.answer,
            "confidence": log.confidence,
            "reason": log.reason,
            "sources": sources,
            "created_at": log.created_at,
        })

    return result


# ---------------- ANALYTICS ----------------

@app.get("/analytics")
def analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)

    total_queries = db.query(QueryLog).count()

    return {
        "total_queries": total_queries
    }