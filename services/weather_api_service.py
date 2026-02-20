from typing import Any, Literal
from datetime import datetime, timedelta, timezone
import requests
from json.decoder import JSONDecodeError
from core.models import Weather, WeatherType
from core.exceptions import ApiServiceError, ApiConnectionError, ApiTimeoutError
from utils.coordinates import Coordinates
from core.config import settings

def get_weather(coordinates: Coordinates) -> tuple[Weather, dict[str, Any]]:
    """Requests weather in OpenWeather API and returns parsed data and raw payload"""
    openweather_response = (
        _get_openweather_response(latitude=coordinates.latitude,
                                  longitude=coordinates.longitude))
    weather = _parse_open_weather_response(openweather_response)
    return weather, openweather_response


def _get_openweather_response(latitude: float, longitude: float) -> dict[str, Any]:
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": settings.OPENWEATHER_API_KEY,
        "units": "metric",
        "lang": "ru",
    }
    try:
        response = requests.get(
            settings.OPENWEATHER_BASE_URL,
            params=params,
            timeout=settings.REQUEST_TIMEOUT_SECONDS,
        )
    except requests.Timeout as exc:
        raise ApiTimeoutError from exc
    except requests.RequestException as exc:
        raise ApiConnectionError from exc
    if response.status_code != 200:
        raise ApiServiceError
    try:
        return response.json()
    except JSONDecodeError as exc:
        raise ApiServiceError from exc


def _parse_open_weather_response(openweather_dict: dict[str, Any]) -> Weather:
    return Weather(
        temperature=_parse_temperature(openweather_dict),
        weather_type=_parse_weather_type(openweather_dict),
        sunrise=_parse_suntime(openweather_dict, "sunrise"),
        sunset=_parse_suntime(openweather_dict, "sunset"),
        city=_parse_city(openweather_dict)
    )


def _parse_temperature(openweather_dict: dict[str, Any]) -> int:
    try:
        return round(openweather_dict["main"]["temp"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ApiServiceError from exc


def _parse_weather_type(openweather_dict: dict[str, Any]) -> WeatherType:
    try:
        weather_type_id = str(openweather_dict["weather"][0]["id"])
    except (IndexError, KeyError, TypeError) as exc:
        raise ApiServiceError from exc
    weather_types = {
        "2": WeatherType.THUNDERSTORM,
        "3": WeatherType.DRIZZLE,
        "5": WeatherType.RAIN,
        "6": WeatherType.SNOW,
        "7": WeatherType.FOG,
        "800": WeatherType.CLEAR,
        "80": WeatherType.CLOUDS
    }

    for _id, _weather_type in weather_types.items():
        if weather_type_id.startswith(_id):
            return _weather_type
    raise ApiServiceError


def _parse_timezone(openweather_dict: dict[str, Any]) -> timezone:
    try:
        timezone_offset_seconds = int(openweather_dict["timezone"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ApiServiceError from exc
    try:
        return timezone(timedelta(seconds=timezone_offset_seconds))
    except ValueError as exc:
        raise ApiServiceError from exc


def _parse_suntime(
    openweather_dict: dict[str, Any],
    time_key: Literal["sunrise"] | Literal["sunset"],
) -> datetime:
    city_timezone = _parse_timezone(openweather_dict)
    try:
        timestamp = openweather_dict["sys"][time_key]
    except (KeyError, TypeError) as exc:
        raise ApiServiceError from exc
    try:
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone(city_timezone)
    except (TypeError, ValueError, OSError) as exc:
        raise ApiServiceError from exc


def _parse_city(openweather_dict: dict[str, Any]) -> str:
    try:
        city = openweather_dict["name"]
    except (KeyError, TypeError) as exc:
        raise ApiServiceError from exc
    if not isinstance(city, str) or not city:
        raise ApiServiceError
    return city


if __name__ == '__main__':
    print(get_weather(Coordinates(latitude=57.3, longitude=49.4))[0])
