import os
from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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

    class Config:
        env_file = "./.env.example"
        case_sensitive = True


class DevSettings(Settings):
    ENV: str = "dev"

    class Config:
        env_file = "./.env.example"
        case_sensitive = True


class TestSettings(Settings):
    ENV: str = "test"

    class Config:
        env_file = "./.env.testexample"
        case_sensitive = True


# TODO: Think about overwriting config for tests from file
def get_settings(env: str) -> Settings:
    """
    Return the settings object based on the environment.

    Parameters:
        env (str): The environment to retrieve the settings for. Defaults to "dev".

    Returns:
        Settings: The settings object based on the environment.

    Raises:
        ValueError: If the environment is invalid.
    """
    if env.lower() == "dev":
        return DevSettings()
    if env.lower() == "test":
        return TestSettings()

    raise ValueError("Invalid environment. Must be 'dev' or 'test'.")


ENV_NAME = os.environ.get("ENV", "dev")

settings = get_settings(ENV_NAME)
