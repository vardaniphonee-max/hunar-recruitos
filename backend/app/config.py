from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./recruitos.db")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    demo_mode: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    hunar_api_key: str | None = os.getenv("HUNAR_API_KEY")
    hunar_base_url: str = os.getenv(
        "HUNAR_BASE_URL", "https://api.voice.hunar.ai/external/v1"
    )
    hunar_agent_id: str | None = os.getenv("HUNAR_AGENT_ID")
    public_api_url: str | None = os.getenv("PUBLIC_API_URL")
    apollo_api_key: str | None = os.getenv("APOLLO_API_KEY")
    apollo_base_url: str = os.getenv("APOLLO_BASE_URL", "https://api.apollo.io/api/v1")
    recruiting_company_name: str = os.getenv("RECRUITING_COMPANY_NAME", "Hunar RecruitOS Demo")
    webhook_tolerance_seconds: int = 300


settings = Settings()
