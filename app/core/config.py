from pydantic_settings import BaseSettings, SettingsConfigDict

# BaseSetting을 상속해서 환경변수나 .env 파일에서 값을 가지고 옴, pydantic 계열
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore") # .env를 읽어라

    database_url: str = "postgresql+psycopg://tj_user:tj_password@localhost:5432/trade_journal"
    session_secret: str = "change-me"
    session_https_only: bool = False
    cors_origins: str = "http://localhost:5173"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
