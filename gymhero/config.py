import os

from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from gymhero.log import get_logger

log = get_logger(__name__)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env.dev", env_file_encoding="utf-8", case_sensitive=True
    )

    API_VERSION: str
    PROJECT_NAME: str
    ENV: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

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
    model_config = SettingsConfigDict(
        env_file="./.env.dev", env_file_encoding="utf-8", case_sensitive=True
    )
    ENV: str = "dev"


class ContainerTestSettings(Settings):
    model_config = SettingsConfigDict(
        env_file="./.env.test", env_file_encoding="utf-8", case_sensitive=True
    )
    ENV: str = "test"


class LocalTestSettings(Settings):
    model_config = SettingsConfigDict(
        env_file="./.env.test.local", env_file_encoding="utf-8", case_sensitive=True
    )
    ENV: str = "test"


class LocalDevSettings(Settings):
    model_config = SettingsConfigDict(
        env_file="./.env.local", env_file_encoding="utf-8", case_sensitive=True
    )
    ENV: str = "local"


def get_settings(env: str = "dev") -> Settings:
    """
    Return the settings object based on the environment.

    Parameters:
        env (str): The environment to retrieve the settings for. Defaults to "dev".

    Returns:
        Settings: The settings object based on the environment.

    Raises:
        ValueError: If the environment is invalid.
    """
    log.debug("getting settings for env: %s", env)

    if env.lower() in ["dev", "d", "development"]:
        return ContainerDevSettings()
    if env.lower() in ["test", "t", "testing"]:
        return ContainerTestSettings()
    if env.lower() in ["local", "l"]:
        return LocalDevSettings()

    raise ValueError("Invalid environment. Must be 'dev' or 'test' ,'local'.")


_env = os.environ.get("ENV", "local")

settings = get_settings(env=_env)
