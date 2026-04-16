from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LOTR Shop API"
    app_version: str = "0.1.0"

    environment: str = "development"
    debug: bool = True

    database_url: str = Field(..., alias="DATABASE_URL")
    test_database_url: str | None = Field(default=None, alias="TEST_DATABASE_URL")

    secret_key: str = Field(..., alias="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    testing_routes_enabled: bool = Field(default=True, alias="TESTING_ROUTES_ENABLED")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    @property
    def is_test(self) -> bool:
        return self.environment.lower() == "test"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


settings = Settings()