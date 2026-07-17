from __future__ import annotations

import asyncio

from logging.config import fileConfig

from alembic import context

from sqlalchemy import (
    pool,
)

from sqlalchemy.ext.asyncio import (
    async_engine_from_config,
)


from app.core.config import settings

from app.core.database import Base


# Import models
from app.models.document import DocumentMetadata



config = context.config


if config.config_file_name:

    fileConfig(
        config.config_file_name
    )


target_metadata = Base.metadata



def run_migrations_offline():

    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )


    with context.begin_transaction():

        context.run_migrations()



def do_run_migrations(connection):

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )


    with context.begin_transaction():

        context.run_migrations()



async def run_migrations_online():

    connectable = (
        async_engine_from_config(
            {
                "sqlalchemy.url":
                    settings.DATABASE_URL
            },
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    )


    async with connectable.connect() as connection:

        await connection.run_sync(
            do_run_migrations
        )


    await connectable.dispose()



if context.is_offline_mode():

    run_migrations_offline()

else:

    asyncio.run(
        run_migrations_online()
    )