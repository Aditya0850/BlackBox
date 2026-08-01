from __future__ import with_statement
import logging
from logging.config import fileConfig
import os
import sys
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from sqlalchemy import text
from alembic import context

# Add the src directory to the path so we can import our config
sys.path.append(str(Path(__file__).parent.parent / "src"))

from config import get_settings

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
# We don't have any models yet, so we set to None.
# When we start adding models, we'll import them here.
target_metadata = None

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
    # def process_revision_directives(context, revision, directives):
    #     if getattr(config.cmd_opts, 'autogenerate', False):
    #         if directives[0]:
    #             logger.info("No changes in schema detected.")

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            # We'll run our custom migration steps here
            # Create schemas and role if they don't exist
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS intel"))
            connection.execute(text("CREATE SCHEMA IF NOT EXISTS audit"))
            # Create a role for the audit schema with INSERT/SELECT only
            # We'll create a role named 'audit_writer' that the application will use
            # But note: the application will use a different role for the intel schema.
            # For simplicity, we'll create a role that can be used by the application
            # and then grant appropriate privileges.
            # However, the requirement is that the audit role cannot UPDATE or DELETE.
            # We'll create a role and grant it INSERT and SELECT on audit schema.
            # We'll also need to create a role for the intel schema (for application use)
            # but that will be done in a later migration when we create tables.
            # For now, we just create the schemas and the audit role with restricted privileges.

            # Check if role exists, if not create it
            # We'll use a role named 'blackbox_app' for the application to connect as.
            # But the audit events should be written by a role that only has INSERT/SELECT on audit.
            # We'll create two roles: one for the application (with full access to intel) and
            # one for audit writes (with only INSERT/SELECT on audit).
            # However, the application will need to write to audit events, so the application role
            # must have INSERT on audit.events (but we don't have the table yet).
            # We'll handle that when we create the table.

            # For now, let's create a role for the application and grant it usage on schemas.
            # We'll refine this in later migrations.

            # Create a role for the application (if not exists)
            connection.execute(text("DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'blackbox_app') THEN CREATE ROLE blackbox_app LOGIN PASSWORD 'blackbox_app_password'; END IF; END $$;"))
            # Grant usage on schemas to the application role
            connection.execute(text("GRANT USAGE ON SCHEMA intel TO blackbox_app"))
            connection.execute(text("GRANT USAGE ON SCHEMA audit TO blackbox_app"))

            # Create a role for audit writes (if not exists) - this role will be used by the application to write audit events
            # but we will restrict it later when we have the table.
            connection.execute(text("DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'audit_writer') THEN CREATE ROLE audit_writer LOGIN PASSWORD 'audit_writer_password'; END IF; END $$;"))
            # Grant usage on audit schema to audit_writer
            connection.execute(text("GRANT USAGE ON SCHEMA audit TO audit_writer"))

            # We will grant specific privileges on tables when they are created in later migrations.

    # Note: The above transaction will be committed when the context exits.

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()