from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


SignInMethod = Literal["http", "none"]
StatsPayload = dict[str, float | int | str]


@dataclass(slots=True)
class SignInResult:
    success: bool
    message: str
    method: SignInMethod
    cookie_expired: bool = False
    statistics: StatsPayload | None = None
    updated_cookie: str | None = None


@dataclass(frozen=True, slots=True)
class AccountConfig:
    index: int
    display_name: str
    cookie: str = ""


@dataclass(frozen=True, slots=True)
class SignInStats:
    total_amount: float
    average: float
    days_count: int
    period: str

    def to_payload(self) -> StatsPayload:
        return {
            "total_amount": self.total_amount,
            "average": self.average,
            "days_count": self.days_count,
            "period": self.period,
        }
