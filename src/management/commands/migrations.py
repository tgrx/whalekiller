import asyncio
import contextlib
import json
from pathlib import Path
from typing import Generator
from typing import Set

import asyncpg
from asyncpg import Connection

from framework.config import settings
from framework.dirs import DIR_MIGRATIONS
from management.commands.abstract import ManagementCommand


class MigrationsCommand(ManagementCommand):
    name = "migrations"
    help = (
        "DB migrations command."
        " If called without arguments,"
        " displays the ids of applied migrations."
    )
    arguments = {
        "--apply": "Apply the missing migrations",
    }

    def __call__(self):
        url = settings.DATABASE_URL
        if not url:
            raise RuntimeError("database is not configured")

        loop = asyncio.get_event_loop()

        if self.option_is_active("--apply"):
            task = self.apply_migrations()
        else:
            task = self.display_applied_versions()

        loop.run_until_complete(task)

    @staticmethod
    @contextlib.asynccontextmanager
    async def db_connect(txn=False):
        conn: Connection = await asyncpg.connect(
            command_timeout=30,  # FIXME: magic
            dsn=settings.DATABASE_URL,
            ssl="prefer",
            timeout=30,  # FIXME: magic
        )

        try:
            if txn:
                async with conn.transaction():
                    yield conn
            else:
                yield conn
        finally:
            await conn.close(timeout=30)  # FIXME: magic

    async def display_applied_versions(self) -> None:
        async with self.db_connect(txn=True) as conn:
            result = {
                version: DIR_MIGRATIONS / version
                for version in await self.fetch_applied_versions(conn)
            }

        result = {
            v: p.as_posix() if p.is_file() else "(file is missing)"
            for v, p in result.items()
        }

        print(json.dumps(result, sort_keys=True, indent=2))

    async def apply_migrations(self) -> None:
        async with self.db_connect() as conn:
            async with conn.transaction():
                applied_versions = await self.fetch_applied_versions(conn)

            async with conn.transaction():
                for migration in self.list_migrations_paths():
                    if migration.name in applied_versions:
                        print(
                            f"\N{HEAVY CHECK MARK}\N{VARIATION SELECTOR-16}\t{migration}"
                        )
                        continue

                    try:
                        await self.apply_single_migration(migration, conn)
                    except Exception:
                        print(f"\N{CROSS MARK}\t{migration}")
                        raise
                    else:
                        print(f"\N{WHITE HEAVY CHECK MARK}\t{migration}")

    @staticmethod
    async def apply_single_migration(migration, conn) -> None:
        with migration.open("r") as dst:
            statements = dst.read()
            for sql in statements.split(";"):
                sql = sql.strip()
                if not sql:
                    continue
                await conn.execute(f"{sql};")

            sql = """insert into migrations(version) values($1)"""
            await conn.execute(sql, migration.name)

    @staticmethod
    def list_migrations_paths() -> Generator[Path, None, None]:
        for path in sorted(DIR_MIGRATIONS.glob("*.sql")):
            yield path

    @staticmethod
    async def fetch_applied_versions(conn: Connection) -> Set[str]:
        versions = set()

        sql = """select version from migrations;"""

        try:
            async for record in conn.cursor(sql):
                versions.add(record["version"])
        except asyncpg.UndefinedTableError as err:
            if "migrations" not in str(err):
                raise

        return versions
