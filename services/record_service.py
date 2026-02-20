from datetime import datetime
from typing import Any, Callable, Mapping

from core.models import Weather
from repositories.uow import UnitOfWork


class RecordService:
    def __init__(self, uow_factory: Callable[[], UnitOfWork]):
        self._uow_factory = uow_factory

    def record_error(
        self,
        *,
        requested_at: datetime,
        latitude: float | None,
        longitude: float | None,
        endpoint: str,
        error_type: str,
        error_message: str,
        duration_ms: int | None,
    ) -> None:
        with self._uow_factory() as uow:
            uow.repo.insert_request(
                requested_at=requested_at,
                latitude=latitude,
                longitude=longitude,
                endpoint=endpoint,
                status="error",
                error_type=error_type,
                error_message=error_message,
                duration_ms=duration_ms,
            )

    def record_success(
        self,
        *,
        requested_at: datetime,
        latitude: float,
        longitude: float,
        endpoint: str,
        duration_ms: int,
        weather: Weather,
        payload: Mapping[str, Any],
    ) -> None:
        with self._uow_factory() as uow:
            request_id = uow.repo.insert_request(
                requested_at=requested_at,
                latitude=latitude,
                longitude=longitude,
                endpoint=endpoint,
                status="ok",
                error_type=None,
                error_message=None,
                duration_ms=duration_ms,
            )
            uow.repo.insert_response(
                request_id=request_id,
                city=weather.city,
                temperature=weather.temperature,
                weather_type=weather.weather_type.value,
                sunrise=weather.sunrise,
                sunset=weather.sunset,
                payload=payload,
            )
