import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from sqlalchemy.engine import make_url

from alembic import context
from app.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url() -> str:
    explicit_alembic_url = os.environ.get("ALEMBIC_DATABASE_URL")
    if explicit_alembic_url:
        return explicit_alembic_url
    return os.environ["DATABASE_URL"]


def get_sync_database_url() -> str:
    database_url = get_database_url()
    sync_url = make_url(database_url).set(drivername="postgresql+psycopg2")
    print("ALEMBIC DATABASE_URL =", database_url)
    print("ALEMBIC SYNC URL =", sync_url.render_as_string(hide_password=False))
    return sync_url.render_as_string(hide_password=False)


def run_migrations_offline() -> None:
    url = get_sync_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        get_sync_database_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()