import os

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from gymhero.log import get_logger

log = get_logger(__name__)


class Settings(BaseSettings):
    # Committed dummy defaults; a git-ignored `.env` or real env vars override them.
    model_config = SettingsConfigDict(
        env_file=".env.defaults", env_file_encoding="utf-8", case_sensitive=True
    )

    API_VERSION: str
    PROJECT_NAME: str
    ENV: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    SERVER_HOST: str
    SERVER_PORT: int

    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int

    FIRST_SUPERUSER_USERNAME: str
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str


class ContainerDevSettings(Settings):
    ENV: str = "dev"


class ContainerTestSettings(Settings):
    # The database comes from a testcontainer (POSTGRES_* injected at runtime);
    # everything else falls back to the committed defaults.
    ENV: str = "test"


class ProductionSettings(Settings):
    # Real deployments override every value via real env vars / a git-ignored `.env`.
    ENV: str = "production"


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
