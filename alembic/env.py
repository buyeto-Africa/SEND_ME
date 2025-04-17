import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from alembic import context
from models import Base  # Adjust import based on where your Base model is defined
from core.config import DATABASE_URL  # Import your database URL from config

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
# Target metadata will be the base metadata from SQLAlchemy
target_metadata = Base.metadata

# This is used to configure the database URL (from alembic.ini or directly from config)
def get_database_url():
    return config.get_main_option("sqlalchemy.url") or DATABASE_URL

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    In this mode, no Engine is needed, and we don't need a DBAPI
    for executing raw SQL directly.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this mode, we create an Engine and associate a connection with the context.
    """
    # Create an async engine
    connectable = create_async_engine(get_database_url(), echo=True)

    async with connectable.connect() as connection:
        # We need to use the connection for async migrations
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        async with connection.begin():
            await context.run_migrations()


def run_migrations():
    """Check if Alembic is running in offline or online mode
    and trigger the respective method.
    """
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        # Ensure `run_migrations_online()` is executed in an event loop
        asyncio.run(run_migrations_online())


# Trigger migrations depending on mode (offline or online)
run_migrations()
