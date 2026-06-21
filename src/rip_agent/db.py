from collections.abc import Callable
from contextlib import AbstractContextManager
from typing import Any


def default_connection_factory(dsn: str) -> Callable[[], AbstractContextManager[Any]]:
    """Builds a psycopg connection factory for the given DSN.

    Shared by ingestion (PgVectorStore) and retrieval (bm25/dense search) so
    both talk to Postgres the same way, with the connection lazily imported
    and injectable in tests.
    """

    def factory() -> AbstractContextManager[Any]:
        import psycopg

        return psycopg.connect(dsn)

    return factory
