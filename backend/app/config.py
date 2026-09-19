import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """환경 변수 기반 설정. 서비스 계정 키 등 민감 정보는 코드에 직접 두지 않는다."""

    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_base_url: str | None = os.getenv("OPENAI_BASE_URL") or None
    firebase_service_account_json: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "")
    allowed_origins: list[str] = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    ]
    chat_model: str = os.getenv("CHAT_MODEL", "gpt-4o-mini")
    chat_max_tokens: int = int(os.getenv("CHAT_MAX_TOKENS", "500"))


settings = Settings()
