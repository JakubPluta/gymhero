import os

import dotenv
import pytest
from pydantic import SecretStr

from gymhero.config import get_settings

dotenv.load_dotenv(".env.defaults")


def test_properly_read_config(test_settings) -> None:
    for key in type(test_settings).model_fields:
        value = getattr(test_settings, key)
        actual = value.get_secret_value() if isinstance(value, SecretStr) else str(value)
        assert actual == os.environ[key]


def test_get_settings_supports_production(monkeypatch) -> None:
    # ENV env var (set to "test" by the test runner) would otherwise override the
    # class default, so drop it to exercise ProductionSettings' own default.
    monkeypatch.delenv("ENV", raising=False)
    assert get_settings("production").ENV == "production"


def test_get_settings_rejects_unknown_env() -> None:
    with pytest.raises(ValueError, match="Invalid environment"):
        get_settings("staging")
