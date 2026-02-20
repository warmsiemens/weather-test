from typing import Protocol, Mapping, Any
from datetime import datetime


class WeatherRepository(Protocol):
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
        ...

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
        ...
