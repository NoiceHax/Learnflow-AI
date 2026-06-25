"""Application settings, loaded from environment / .env file."""
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_DIR / ".env"),
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # Prefer backend/.env over machine-wide DATABASE_URL so local SQLite works out of the box.
        return init_settings, dotenv_settings, env_settings, file_secret_settings

    app_name: str = "Astra"
    api_prefix: str = "/api"

    # Database: SQLite by default, swap DATABASE_URL for Supabase Postgres.
    database_url: str = "sqlite:///./astra.db"

    # Auth
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    # External LLM (Socrates + remediation question generation).
    use_ai: bool = Field(default=True, validation_alias="USE_AI")
    nvidia_api_key: str = ""
    # Comma-separated key pool — parallel requests rotate across keys (see nvidia_keys.py).
    nvidia_api_keys: str = Field(default="", validation_alias="NVIDIA_API_KEYS")
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
    # Comma-separated fallback chain (tried in order). Overrides nvidia_model when set.
    nvidia_models: str = ""
    nvidia_thinking: bool = True
    # Faster chain for bulk question generation (pregenerate / backups). Falls back to defaults if unset.
    nvidia_question_models: str = Field(default="", validation_alias="NVIDIA_QUESTION_MODELS")
    nvidia_question_timeout_sec: float = Field(default=90.0, validation_alias="NVIDIA_QUESTION_TIMEOUT_SEC")
    # Per API key: max requests per minute (NVIDIA NIM ~40 RPM; default 35 for headroom).
    nvidia_rpm_per_key: float = Field(default=35.0, validation_alias="NVIDIA_RPM_PER_KEY")

    # Practice quiz: questions shown per session; correct answers trigger AI replacements.
    practice_pool_size: int = Field(default=5, validation_alias="PRACTICE_POOL_SIZE")
    # Hard floor: never serve a quiz with fewer than this many questions.
    min_quiz_questions: int = Field(default=2, validation_alias="MIN_QUIZ_QUESTIONS")
    # Max previously-wrong questions mixed into each practice round (rest are fresh).
    practice_reinforce_wrong: int = Field(default=1, validation_alias="PRACTICE_REINFORCE_WRONG")
    # Live NVIDIA calls while loading practice (slow; default uses DB backup bank only).
    practice_live_api_on_load: bool = Field(default=False, validation_alias="PRACTICE_LIVE_API_ON_LOAD")

    # Offline backup bank: target AI questions per chapter = multiplier × seed count.
    chapter_backup_multiplier: float = Field(default=2.0, validation_alias="CHAPTER_BACKUP_MULTIPLIER")

    # Pilot / multi-user testing: only N chapters per subject + pre-generated AI bank.
    pilot_mode: bool = Field(default=True, validation_alias="PILOT_MODE")
    pilot_chapters_per_subject: int = Field(default=3, validation_alias="PILOT_CHAPTERS_PER_SUBJECT")
    pilot_ai_questions_per_chapter: int = Field(
        default=35, validation_alias="PILOT_AI_QUESTIONS_PER_CHAPTER"
    )
    # Optional override: comma-separated chapter slugs (else first 3 per subject).
    pilot_chapter_slugs: str = Field(default="", validation_alias="PILOT_CHAPTER_SLUGS")

    # CORS — production frontend + optional extra origins (comma-separated, env CORS_ORIGINS).
    frontend_url: str = "http://localhost:3000"
    cors_origins_csv: str = Field(default="", validation_alias="CORS_ORIGINS")

    # Rate Limiting & Abuse Protection
    rate_limit_socrates_minute: int = Field(default=5, validation_alias="RATE_LIMIT_SOCRATES_MINUTE")
    rate_limit_socrates_daily: int = Field(default=50, validation_alias="RATE_LIMIT_SOCRATES_DAILY")
    rate_limit_question_gen_minute: int = Field(default=3, validation_alias="RATE_LIMIT_QUESTION_GEN_MINUTE")
    rate_limit_question_gen_daily: int = Field(default=20, validation_alias="RATE_LIMIT_QUESTION_GEN_DAILY")

    @property
    def database_url_resolved(self) -> str:
        """Normalize Postgres URLs for SQLAlchemy (psycopg3 or psycopg2 on Render/Neon)."""
        url = self.database_url.strip()
        if not (url.startswith("postgres://") or url.startswith("postgresql://")):
            return url
        if "+" in url.split("://", 1)[0]:
            return url

        driver = "postgresql+psycopg"
        try:
            import psycopg  # noqa: F401
        except ImportError:
            try:
                import psycopg2  # noqa: F401
                driver = "postgresql+psycopg2"
            except ImportError:
                driver = "postgresql"

        if url.startswith("postgres://"):
            return driver + "://" + url[len("postgres://") :]
        return url.replace("postgresql://", f"{driver}://", 1)

    @property
    def resolved_cors_origins(self) -> list[str]:
        origins: set[str] = set()
        for raw in (
            self.frontend_url,
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ):
            o = raw.strip().rstrip("/")
            if o:
                origins.add(o)
        if self.cors_origins_csv.strip():
            for part in self.cors_origins_csv.split(","):
                o = part.strip().rstrip("/")
                if o:
                    origins.add(o)
        return sorted(origins)

    @property
    def cors_origin_regex(self) -> str:
        """Vercel previews + local dev (any port / LAN IP)."""
        return (
            r"https://[\w-]+\.vercel\.app"
            r"|http://(localhost|127\.0\.0\.1)(:\d+)?"
            r"|http://100\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?"
            r"|http://192\.168\.\d{1,3}\.\d{1,3}(:\d+)?"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# Drop instruct / coder / vision-instruct endpoints from any chain (chat + question gen).
_EXCLUDED_NVIDIA_MODEL_TOKENS: tuple[str, ...] = (
    "-instruct",
    "vision-instruct",
    "/coder",
    "coder-",
    "coder/",
)


def _is_allowed_nvidia_model(model_id: str) -> bool:
    m = model_id.strip().lower()
    if not m:
        return False
    return not any(token in m for token in _EXCLUDED_NVIDIA_MODEL_TOKENS)


def filter_nvidia_models(models: list[str]) -> list[str]:
    """Dedupe and remove instruct/coder/vision models."""
    seen: set[str] = set()
    out: list[str] = []
    for model in models:
        m = model.strip()
        if not m or not _is_allowed_nvidia_model(m):
            continue
        key = m.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(m)
    return out


def filter_question_gen_models(models: list[str]) -> list[str]:
    """Drop reasoning / huge models that leak prose instead of JSON."""
    skip_tokens = ("reasoning", "nemotron-3-super", "675b", "397b", "480b")
    out: list[str] = []
    for m in filter_nvidia_models(models):
        lower = m.lower()
        if any(token in lower for token in skip_tokens):
            continue
        out.append(m)
    return out


# Socrates chat fallback chain — dashboard score order (high → low), no instruct models.
DEFAULT_NVIDIA_MODEL_CHAIN: tuple[str, ...] = (
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
    "openai/gpt-oss-120b",
    "stepfun-ai/step-3.5-flash",
    "nvidia/nemotron-3-super-120b-a12b",
    "moonshotai/kimi-k2.6",
    "z-ai/glm-5.1",
    "deepseek-ai/deepseek-v4-flash",
    "deepseek-ai/deepseek-v4-pro",
    "minimaxai/minimax-m2.7",
    "mistralai/mistral-medium-3.5-128b",
    "qwen/qwen3.5-397b-a17b",
    "qwen/qwen3.5-122b-a10b",
)

# Question generation — same 4 models as chat, dashboard score order.
DEFAULT_NVIDIA_QUESTION_MODEL_CHAIN: tuple[str, ...] = (
    "stepfun-ai/step-3.5-flash",
    "deepseek-ai/deepseek-v4-flash",
    "deepseek-ai/deepseek-v4-pro",
    "mistralai/mistral-medium-3.5-128b",
)


def nvidia_api_keys_list() -> list[str]:
    """Resolved NVIDIA API keys (pool first, then single NVIDIA_API_KEY)."""
    if settings.nvidia_api_keys.strip():
        keys = [k.strip() for k in settings.nvidia_api_keys.split(",") if k.strip()]
        if keys:
            return keys
    if settings.nvidia_api_key.strip():
        return [settings.nvidia_api_key.strip()]
    return []


def nvidia_model_chain() -> list[str]:
    """Ordered NVIDIA model IDs to attempt (first success wins)."""
    if settings.nvidia_models.strip():
        chain = [m.strip() for m in settings.nvidia_models.split(",") if m.strip()]
    elif settings.nvidia_model.strip():
        primary = settings.nvidia_model.strip()
        rest = [m for m in DEFAULT_NVIDIA_MODEL_CHAIN if m != primary]
        chain = [primary, *rest]
    else:
        chain = list(DEFAULT_NVIDIA_MODEL_CHAIN)
    return filter_nvidia_models(chain)


def nvidia_question_model_chain() -> list[str]:
    """Model chain for bulk JEE question generation (pregenerate, backups)."""
    if settings.nvidia_question_models.strip():
        chain = [m.strip() for m in settings.nvidia_question_models.split(",") if m.strip()]
    else:
        chain = list(DEFAULT_NVIDIA_QUESTION_MODEL_CHAIN)
    return filter_question_gen_models(chain)
