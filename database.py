from types import TracebackType
from typing import Callable

import psycopg2
from core.config import settings
from repositories.base import WeatherRepository
from repositories.weather_repo import PostgresWeatherRepository
from repositories.uow import UnitOfWork


def get_connection():
    return psycopg2.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )


class PostgresUnitOfWork(UnitOfWork):
    def __init__(self, connection_factory: Callable = get_connection):
        self._connection_factory = connection_factory
        self._conn = None
        self.repo: WeatherRepository

    def __enter__(self) -> "PostgresUnitOfWork":
        self._conn = self._connection_factory()
        self.repo = PostgresWeatherRepository(self._conn)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc_type is None:
            self._conn.commit()
        else:
            self._conn.rollback()
        self._conn.close()


def init_db(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS requests (
                id SERIAL PRIMARY KEY,
                requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                latitude DOUBLE PRECISION,
                longitude DOUBLE PRECISION,
                endpoint TEXT NOT NULL,
                status TEXT NOT NULL,
                error_type TEXT,
                error_message TEXT,
                duration_ms INTEGER
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
                id SERIAL PRIMARY KEY,
                request_id INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
                received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                city TEXT,
                temperature INTEGER,
                weather_type TEXT,
                sunrise TIMESTAMPTZ,
                sunset TIMESTAMPTZ,
                payload JSONB
            );
            """
        )
    conn.commit()
