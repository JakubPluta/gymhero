import os
import sys
from logging.config import fileConfig
import logging

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from gymhero.models import Base  # pylint: wrong-import-position

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.

fileConfig(config.config_file_name)


logger = logging.getLogger(__name__)


logger.info("Config file name: %s", config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata


target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    dbname = config.config_ini_section
    section = config.get_section(config.config_ini_section)
    logger.info("Running offline migration for db: %s", dbname)
    # Inject environment variable values into connection string
    url = section["sqlalchemy.url"]
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    dbname = config.config_ini_section
    section = config.get_section(config.config_ini_section)
    logger.info("Running online migration for db: %s", dbname)
    # Inject environment variable values into connection string
    url = section["sqlalchemy.url"]
    section["sqlalchemy.url"] = url
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
