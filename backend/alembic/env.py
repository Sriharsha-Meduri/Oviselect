"""Alembic env — reads DATABASE_URL from environment."""

import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Ensure the backend package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = os.getenv("DATABASE_URL", "postgresql://oviguide:oviguide_secret@db:5432/oviguide")
config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    context.configure(url=database_url, target_metadata=None, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(database_url)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=None)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

