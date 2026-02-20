from typing import NamedTuple

import geocoder

from core.config import settings
from core.exceptions import CantGetCoordinates


class Coordinates(NamedTuple):
    latitude: float
    longitude: float


def get_coordinates() -> Coordinates:
    """returns current coordinates using geocoder"""
    if settings.LATITUDE and settings.LONGITUDE:
        try:
            return Coordinates(
                latitude=float(settings.LATITUDE),
                longitude=float(settings.LONGITUDE),
            )
        except ValueError as exc:
            raise CantGetCoordinates from exc

    try:
        latitude, longitude = geocoder.ip("me").latlng
    except Exception as exc:
        raise CantGetCoordinates from exc

    if latitude is None or longitude is None:
        raise CantGetCoordinates

    return Coordinates(latitude=latitude, longitude=longitude)
