import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Mapping

from core.config import settings
from core.models import Weather
from core.exceptions import (
    ApiConnectionError,
    ApiServiceError,
    ApiTimeoutError,
    CantGetCoordinates,
)
from database import PostgresUnitOfWork, get_connection, init_db
from services.record_service import RecordService
from services.weather_api_service import get_weather
from utils.coordinates import Coordinates, get_coordinates
from utils.logging import setup_error_logger
from utils.weather_formatter import format_weather


@dataclass(frozen=True)
class ApiErrorContext:
    error_type: str
    error_message: str
    user_message: str
    log_message: str


API_ERROR_CONTEXTS: dict[type[Exception], ApiErrorContext] = {
    ApiTimeoutError: ApiErrorContext(
        error_type="timeout",
        error_message="openweather_timeout",
        user_message="Таймаут запроса погоды",
        log_message="OpenWeather timeout",
    ),
    ApiConnectionError: ApiErrorContext(
        error_type="connection",
        error_message="openweather_connection_error",
        user_message="Ошибка подключения к сервису погоды",
        log_message="OpenWeather connection error",
    ),
    ApiServiceError: ApiErrorContext(
        error_type="api",
        error_message="openweather_error",
        user_message="Не удалось получить погоду по координатам",
        log_message="OpenWeather api error",
    ),
}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def run_once(
    logger: logging.Logger,
    record_service: RecordService,
    *,
    coordinates_provider: Callable[[], Coordinates] = get_coordinates,
    weather_provider: Callable[[Coordinates], tuple[Weather, Mapping[str, Any]]] = get_weather,
    formatter: Callable[[Weather], str] = format_weather,
    now_provider: Callable[[], datetime] = _utc_now,
    perf_counter: Callable[[], float] = time.perf_counter,
    endpoint: str | None = None,
) -> str:
    endpoint = endpoint or settings.OPENWEATHER_BASE_URL
    requested_at = now_provider()
    duration_ms = None
    latitude = None
    longitude = None
    try:
        coordinates = coordinates_provider()
        latitude = coordinates.latitude
        longitude = coordinates.longitude
    except CantGetCoordinates:
        record_service.record_error(
            requested_at=requested_at,
            latitude=latitude,
            longitude=longitude,
            endpoint=endpoint,
            error_type="coordinates",
            error_message="cant_get_coordinates",
            duration_ms=duration_ms,
        )
        return "Не удалось получить координаты"

    started = perf_counter()
    try:
        weather, payload = weather_provider(coordinates)
    except (ApiTimeoutError, ApiConnectionError, ApiServiceError) as exc:
        duration_ms = int((perf_counter() - started) * 1000)
        error_context = API_ERROR_CONTEXTS[type(exc)]
        logger.error(error_context.log_message, exc_info=True)
        record_service.record_error(
            requested_at=requested_at,
            latitude=latitude,
            longitude=longitude,
            endpoint=endpoint,
            error_type=error_context.error_type,
            error_message=error_context.error_message,
            duration_ms=duration_ms,
        )
        return error_context.user_message

    duration_ms = int((perf_counter() - started) * 1000)
    record_service.record_success(
        requested_at=requested_at,
        latitude=latitude,
        longitude=longitude,
        endpoint=endpoint,
        duration_ms=duration_ms,
        weather=weather,
        payload=payload,
    )
    return formatter(weather)


def main() -> None:
    if not settings.OPENWEATHER_API_KEY:
        print("Не задан OPENWEATHER_API_KEY в .env")
        raise SystemExit(1)
    logger = setup_error_logger()
    record_service = RecordService(PostgresUnitOfWork)
    with get_connection() as conn:
        init_db(conn)
    interval_seconds = max(settings.WEATHER_INTERVAL_MINUTES, 1) * 60
    while True:
        print(run_once(logger, record_service))
        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
