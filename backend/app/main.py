"""Astra backend: FastAPI application entrypoint."""
import logging
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import nvidia_api_keys_list, settings
from .database import Base, engine, apply_schema_patches
from .middleware.request_log import RequestLogMiddleware
from .services.llm import active_model, active_provider, ai_requested, credential_configured, probe_llm
from .services.llm_audit import audit_summary
from .routers import (
    analytics,
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

_CORS_ORIGIN_SET = {o.rstrip("/") for o in settings.resolved_cors_origins}
_CORS_ORIGIN_PATTERN = re.compile(settings.cors_origin_regex)


def _cors_headers(request: Request) -> dict[str, str]:
    """Attach CORS on error responses (middleware may not run when we return 500)."""
    origin = request.headers.get("origin")
    if not origin:
        return {}
    normalized = origin.rstrip("/")
    if normalized not in _CORS_ORIGIN_SET and not _CORS_ORIGIN_PATTERN.fullmatch(origin):
        return {}
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
    }

# Create tables on startup (SQLite by default; harmless if they already exist).
Base.metadata.create_all(bind=engine)
apply_schema_patches()


def _log_llm_status() -> None:
    """Print LLM connectivity to the server terminal on startup."""
    provider = active_provider()
    model = active_model()
    logger.info(
        "Loading settings: use_ai=%s | provider=%s | model=%s | credential=%s",
        ai_requested(),
        provider,
        model,
        "present" if credential_configured() else "missing",
    )
    if not ai_requested():
        logger.info(
            "AI startup: USE_AI=false | Socrates=fallback | questions=seed-only | no API calls",
        )
        return
    logger.info(
        "Tip: editing backend/.env requires a server restart (or touch a .py file) for --reload to pick it up"
    )
    status = probe_llm(force=True)
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
    logger.info("CORS allow_origins=%s", settings.resolved_cors_origins)
    logger.info("CORS allow_origin_regex=%s", settings.cors_origin_regex)
    _log_llm_status()
    yield


app = FastAPI(
    title="Astra API",
    description="AI learning platform for JEE Advanced, Grade 12.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=_cors_headers(request),
    )


app.add_middleware(RequestLogMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.resolved_cors_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth, catalog, quiz, assessment, learning_path, lessons, mastery, dashboard, analytics, socrates):
    app.include_router(r.router, prefix=settings.api_prefix)


@app.get("/api/health", tags=["health"])
def health(refresh: bool = False):
    status = probe_llm(force=refresh) if ai_requested() else {
        "configured": credential_configured(),
        "use_ai": False,
        "provider": active_provider(),
        "ok": False,
        "model": active_model(),
        "error": "USE_AI=false",
    }
    configured = status.get("configured", credential_configured())
    connected = status.get("ok", False)
    return {
        "status": "ok",
        "service": settings.app_name,
        "llm": {
            "use_ai": ai_requested(),
            "provider": status.get("provider", active_provider()),
            "configured": configured,
            "connected": connected,
            "model": status.get("model") or active_model(),
            "nvidia_key_pool": len(nvidia_api_keys_list()),
            "error": None if connected else status.get("error"),
        },
        "questions": {
            "mode": "ai+seed" if connected else "seed-only",
            "note": "Quizzes use the seeded bank; AI adds remediation on quiz submit when enabled.",
        },
        "llm_audit": audit_summary(),
    }


@app.get("/", tags=["health"])
def root():
    return {"name": "Astra API", "docs": "/docs"}
