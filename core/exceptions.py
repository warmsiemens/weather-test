class ApiServiceError(Exception):
    """Program cant take current weather"""


class CantGetCoordinates(Exception):
    """Program cant get current coordinates"""


class ApiConnectionError(Exception):
    """Connection error while calling API"""


class ApiTimeoutError(Exception):
    """Timeout while calling API"""
