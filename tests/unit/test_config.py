import os

import dotenv
import pytest

from gymhero.config import get_settings

dotenv.load_dotenv(".env.defaults")


def test_properly_read_config(test_settings):
    """Test whether the config is properly read."""
    for key in [key for key, _ in test_settings.model_fields.items()]:
        assert str(getattr(test_settings, key)) == os.environ[key]


def test_get_settings_supports_production(monkeypatch):
    # ENV env var (set to "test" by the test runner) would otherwise override the
    # class default, so drop it to exercise ProductionSettings' own default.
    monkeypatch.delenv("ENV", raising=False)
    assert get_settings("production").ENV == "production"


def test_get_settings_rejects_unknown_env():
    with pytest.raises(ValueError, match="Invalid environment"):
        get_settings("staging")
