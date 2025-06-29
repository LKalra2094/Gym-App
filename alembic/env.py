import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine.url import make_url
from alembic import context

# Import your Base metadata and settings
from app.models.base import Base
from app.core.config import settings
from app.db.session import engine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata target for 'autogenerate'
target_metadata = Base.metadata


def get_url():
    """Return the database URL, forcing the psycopg2 driver."""
    # Correctly read from settings
    db_url = settings.DATABASE_URL
    if not db_url:
        raise ValueError("DATABASE_URL is not set in the environment or .env file")
    return db_url


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode (no DBAPI required).
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode (requires DBAPI connection).
    """
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# Choose offline vs online mode based on context
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
