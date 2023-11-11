import os

from gymhero.config import settings
import dotenv

dotenv.load_dotenv('.env.example')


def test_properly_read_config():
    for key in [key for key, _ in settings.model_fields.items()]:
        assert str(getattr(settings, key)) == os.environ[key]


