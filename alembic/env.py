import os
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from dotenv import load_dotenv

# Load .env and let it win over any stale DATABASE_URL in this terminal.
load_dotenv(override=True)

config = context.config

# Set DB URL from .env
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL is not set")
config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

# Logging
fileConfig(config.config_file_name)

from app.database import Base
import app.models  # noqa: F401

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async def do_run_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(run_migrations)

    def run_migrations(connection):
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

    asyncio.run(do_run_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
