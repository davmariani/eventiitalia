from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RouteEstimate:
    distance_km: float
    duration_minutes: int
    provider: str


class RoutingProvider(Protocol):
    def estimate_drive(self, origin: tuple[float, float], destination: tuple[float, float]) -> RouteEstimate | None:
        """Return a driving estimate without affecting geographic distance filters."""


class UnconfiguredRoutingProvider:
    def estimate_drive(self, origin: tuple[float, float], destination: tuple[float, float]) -> RouteEstimate | None:
        return None
