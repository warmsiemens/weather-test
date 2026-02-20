from __future__ import annotations

from types import TracebackType
from typing import Protocol

from repositories.base import WeatherRepository


class UnitOfWork(Protocol):
    repo: WeatherRepository

    def __enter__(self) -> "UnitOfWork":
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        ...
