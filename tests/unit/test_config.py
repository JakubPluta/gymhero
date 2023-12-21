import os

import dotenv

dotenv.load_dotenv(".env.test")


def test_properly_read_config(test_settings):
    """Test whether the config is properly read."""
    for key in [key for key, _ in test_settings.model_fields.items()]:
        assert str(getattr(test_settings, key)) == os.environ[key]
