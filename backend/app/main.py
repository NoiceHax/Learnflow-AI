"""Astra backend: FastAPI application entrypoint."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .middleware.request_log import RequestLogMiddleware
from .services.gemini import active_model, active_provider, credential_configured, gemini_requested, probe_gemini
from .services.gemini_audit import audit_summary
from .routers import (
    assessment,
    auth,
    catalog,
    dashboard,
    learning_path,
    lessons,
    mastery,
    quiz,
    socrates,
)

logger = logging.getLogger("uvicorn.error")

# Create tables on startup (SQLite by default; harmless if they already exist).
Base.metadata.create_all(bind=engine)


def _log_gemini_status() -> None:
    """Print LLM connectivity to the server terminal on startup."""
    provider = active_provider()
    model = active_model()
    logger.info(
        "Loading settings: use_ai=%s | provider=%s | model=%s | credential=%s",
        gemini_requested(),
        provider,
        model,
        "present" if credential_configured() else "missing",
    )
    if not gemini_requested():
        logger.info(
            "AI startup: USE_GEMINI=false | Socrates=fallback | questions=seed-only | no API calls",
        )
        return
    logger.info(
        "Tip: editing backend/.env requires a server restart (or touch a .py file) for --reload to pick it up"
    )
    status = probe_gemini(force=True)
    configured = status.get("configured", credential_configured())
    cred_label = "present" if configured else "missing"

    if status.get("ok"):
        logger.info(
            "AI startup: provider=%s | credential=%s | model=%s | connected=yes | Socrates=live AI | questions=ai+seed",
            provider,
            cred_label,
            model,
        )
        return

    err = status.get("error") or "unknown error"
    logger.warning(
        "AI startup: provider=%s | credential=%s | model=%s | connected=no | error=%s | Socrates=fallback | questions=seed-only",
        provider,
        cred_label,
        model,
        err,
    )


@asynccontextmanager
async def lifespan(_app: FastAPI):
    _log_gemini_status()
    yield


app = FastAPI(
    title="Astra API",
    description="AI learning platform for JEE Advanced, Grade 12.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(RequestLogMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.resolved_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth, catalog, quiz, assessment, learning_path, lessons, mastery, dashboard, socrates):
    app.include_router(r.router, prefix=settings.api_prefix)


@app.get("/api/health", tags=["health"])
def health(refresh: bool = False):
    status = probe_gemini(force=refresh) if gemini_requested() else {
        "configured": credential_configured(),
        "use_gemini": False,
        "provider": active_provider(),
        "ok": False,
        "model": active_model(),
        "error": "USE_GEMINI=false",
    }
    configured = status.get("configured", credential_configured())
    connected = status.get("ok", False)
    return {
        "status": "ok",
        "service": settings.app_name,
        "gemini": {
            "use_gemini": gemini_requested(),
            "provider": status.get("provider", active_provider()),
            "configured": configured,
            "connected": connected,
            "model": status.get("model") or active_model(),
            "error": None if connected else status.get("error"),
        },
        "questions": {
            "mode": "ai+seed" if connected else "seed-only",
            "note": "Quizzes use the seeded bank; AI adds remediation on quiz submit when enabled.",
        },
        "gemini_audit": audit_summary(),
    }


@app.get("/", tags=["health"])
def root():
    return {"name": "Astra API", "docs": "/docs"}
