from __future__ import with_statement
import logging
from logging.config import fileConfig
import os
import sys
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from sqlalchemy import text
from alembic import context

# Add the src directory to the path so we can import our config and models
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config import get_settings
from infrastructure.db.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Set the sqlalchemy URL from our settings
settings = get_settings()
# Use asyncpg URL for Alembic? Actually Alembic uses synchronous engine.
# We'll use psycopg2 URL.
config.set_main_option(
    "sqlalchemy.url",
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}",
)

# target_metadata for our 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table_schema="intel",
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # This callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema.
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            if directives[0]:
                logger.info("No changes in schema detected.")

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table_schema="intel",
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            # Run our custom migration steps here
            # Create schemas and role if they don't exist
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS intel"))
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS audit"))
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS notebook"))

            # Create a role for the application
            connection.execute(text("DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'blackbox_app') THEN CREATE ROLE blackbox_app LOGIN PASSWORD 'blackbox_app_password'; END IF; END $$;"))
            connection.execute(text("GRANT USAGE ON SCHEMA intel TO blackbox_app"))
            connection.execute(text("GRANT USAGE ON SCHEMA audit TO blackbox_app"))
            connection.execute(text("GRANT USAGE ON SCHEMA notebook TO blackbox_app"))

            # Create a role for audit writes
            connection.execute(text("DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'audit_writer') THEN CREATE ROLE audit_writer LOGIN PASSWORD 'audit_writer_password'; END IF; END $$;"))
            connection.execute(text("GRANT USAGE ON SCHEMA audit TO audit_writer"))

            context.run_migrations()

    # Note: The above transaction will be committed when the context exits.

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()