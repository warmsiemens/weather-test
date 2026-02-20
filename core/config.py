from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENWEATHER_API_KEY: str
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5/weather"
    REQUEST_TIMEOUT_SECONDS: int
    WEATHER_INTERVAL_MINUTES: int

    LATITUDE: str | None = None
    LONGITUDE: str | None = None

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    ERROR_LOG_FILE: str = "errors.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
