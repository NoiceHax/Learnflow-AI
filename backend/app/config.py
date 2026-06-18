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

    # External LLM: optional enhancement (see USE_GEMINI).
    use_gemini: bool = True  # master switch for all AI network calls
    ai_provider: str = "nvidia"  # nvidia | gemini

    # NVIDIA NIM (OpenAI-compatible): default provider
    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "z-ai/glm-5.1"
    # Comma-separated fallback chain (tried in order). Overrides nvidia_model when set.
    nvidia_models: str = ""
    nvidia_thinking: bool = True

    # Google Gemini: legacy fallback provider
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # CORS — production frontend + optional extra origins (comma-separated, env CORS_ORIGINS).
    frontend_url: str = "http://localhost:3000"
    cors_origins_csv: str = Field(default="", validation_alias="CORS_ORIGINS")

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
        for raw in (self.frontend_url, "http://localhost:3000", "http://127.0.0.1:3000"):
            o = raw.strip().rstrip("/")
            if o:
                origins.add(o)
        if self.cors_origins_csv.strip():
            for part in self.cors_origins_csv.split(","):
                o = part.strip().rstrip("/")
                if o:
                    origins.add(o)
        return sorted(origins)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# NVIDIA NIM models to try in order (highest benchmark rank first).
DEFAULT_NVIDIA_MODEL_CHAIN: tuple[str, ...] = (
    "nvidia/nemotron-3-super-120b-a12b",
    "mistralai/mistral-medium-3.5-128b",
    "openai/gpt-oss-120b",
    "meta/llama-3.2-90b-vision-instruct",
    "mistralai/mistral-large-3-675b-instruct-2512",
    "moonshotai/kimi-k2.6",
    "z-ai/glm-5.1",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
    "stepfun-ai/step-3.5-flash",
    "qwen/qwen3.5-397b-a17b",
    "minimaxai/minimax-m2.7",
)


def nvidia_model_chain() -> list[str]:
    """Ordered NVIDIA model IDs to attempt (first success wins)."""
    if settings.nvidia_models.strip():
        return [m.strip() for m in settings.nvidia_models.split(",") if m.strip()]
    if settings.nvidia_model.strip():
        primary = settings.nvidia_model.strip()
        rest = [m for m in DEFAULT_NVIDIA_MODEL_CHAIN if m != primary]
        return [primary, *rest]
    return list(DEFAULT_NVIDIA_MODEL_CHAIN)
