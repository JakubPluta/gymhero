import os
from typing import Self

from pydantic import EmailStr, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from gymhero.log import get_logger

log = get_logger(__name__)

# Committed dev placeholders that must never be used in production.
_DEV_SECRET_KEY = "dev-only-not-a-real-secret-change-me"
_DEV_POSTGRES_PASSWORD = "gymhero"
_DEV_SUPERUSER_PASSWORD = "changeme"


class Settings(BaseSettings):
    # Committed dummy defaults; a git-ignored `.env` or real env vars override them.
    model_config = SettingsConfigDict(
        env_file=".env.defaults", env_file_encoding="utf-8", case_sensitive=True
    )

    API_VERSION: str
    PROJECT_NAME: str
    ENV: str
    SECRET_KEY: SecretStr
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    SERVER_HOST: str
    SERVER_PORT: int

    # Comma-separated; "*" means "any". Parsed into lists by the properties below.
    CORS_ORIGINS: str
    ALLOWED_HOSTS: str

    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_PORT: int

    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE_SECONDS: int = 1800

    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: SecretStr

    # Plain properties (not computed_field) so the password never lands in
    # model_dump()/serialization.
    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD.get_secret_value()}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def async_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD.get_secret_value()}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def allowed_hosts(self) -> list[str]:
        return [h.strip() for h in self.ALLOWED_HOSTS.split(",") if h.strip()]


class ContainerDevSettings(Settings):
    ENV: str = "dev"


class ContainerTestSettings(Settings):
    # The database comes from a testcontainer (POSTGRES_* injected at runtime);
    # everything else falls back to the committed defaults.
    ENV: str = "test"


class ProductionSettings(Settings):
    # Real deployments override every value via real env vars / a git-ignored `.env`.
    ENV: str = "production"

    @model_validator(mode="after")
    def _reject_committed_dev_defaults(self) -> Self:
        insecure = [
            name
            for name, dummy in (
                ("SECRET_KEY", _DEV_SECRET_KEY),
                ("POSTGRES_PASSWORD", _DEV_POSTGRES_PASSWORD),
                ("FIRST_SUPERUSER_PASSWORD", _DEV_SUPERUSER_PASSWORD),
            )
            if getattr(self, name).get_secret_value() == dummy
        ]
        if insecure:
            raise ValueError(
                "Refusing to start in production with committed dev defaults: "
                + ", ".join(insecure)
            )
        return self


def get_settings(env: str = "dev") -> Settings:
    log.debug("getting settings for env: %s", env)
    if env.lower() in ("dev", "d", "development"):
        return ContainerDevSettings()
    if env.lower() in ("test", "t", "testing"):
        return ContainerTestSettings()
    if env.lower() in ("prod", "production", "p"):
        return ProductionSettings()
    raise ValueError(
        f"Invalid environment {env!r}. Must be 'dev', 'test' or 'production'."
    )


# The app runs in Docker (ENV=dev via docker-compose); tests set ENV=test.
_env = os.environ.get("ENV", "dev")

settings = get_settings(env=_env)
