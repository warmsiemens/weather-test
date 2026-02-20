from datetime import datetime
from typing import Mapping, Any
from psycopg2 import extras
from repositories.base import WeatherRepository


class PostgresWeatherRepository(WeatherRepository):
    def __init__(self, conn):
        self._conn = conn

    def insert_request(
        self,
        requested_at: datetime,
        latitude: float | None,
        longitude: float | None,
        endpoint: str,
        status: str,
        error_type: str | None,
        error_message: str | None,
        duration_ms: int | None,
    ) -> int:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO requests (
                    requested_at, latitude, longitude, endpoint, status,
                    error_type, error_message, duration_ms
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (
                    requested_at,
                    latitude,
                    longitude,
                    endpoint,
                    status,
                    error_type,
                    error_message,
                    duration_ms,
                ),
            )
            request_id = cur.fetchone()[0]
        return request_id

    def insert_response(
        self,
        request_id: int,
        city: str,
        temperature: int,
        weather_type: str,
        sunrise: datetime,
        sunset: datetime,
        payload: Mapping[str, Any],
    ) -> None:
        with self._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO responses (
                    request_id, city, temperature, weather_type,
                    sunrise, sunset, payload
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    request_id,
                    city,
                    temperature,
                    weather_type,
                    sunrise,
                    sunset,
                    extras.Json(payload),
                ),
            )
