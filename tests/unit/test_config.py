import os

import dotenv

dotenv.load_dotenv(".env.test")


def test_properly_read_config(test_settings):
    """Test whether the config is properly read."""
    for key in [key for key, _ in test_settings.model_fields.items()]:
        assert str(getattr(test_settings, key)) == os.environ[key]


def test_can_build_postgres_url(test_settings):
    assert (
        f"postgresql://{test_settings.POSTGRES_USER}:{test_settings.POSTGRES_PASSWORD}@{test_settings.POSTGRES_HOST}:{test_settings.POSTGRES_PORT}/{test_settings.POSTGRES_DB}"
        == "postgresql://test:test@localhost:5433/workout"
    )
