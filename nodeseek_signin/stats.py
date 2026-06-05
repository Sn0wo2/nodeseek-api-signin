from __future__ import annotations

import json
import time
from collections.abc import Sequence

from nodeseek_signin.http_client import HttpResponse, HttpSession, NodeSeekHttpClient
from nodeseek_signin.models import SignInStats


class CreditStatsFetcher:
    MAX_PAGES = 10
    REQUEST_DELAY_SECONDS = 0.3

    def __init__(self, http_client: NodeSeekHttpClient, *, enabled: bool) -> None:
        self._http_client = http_client
        self._enabled = enabled

    def fetch(self, cookie: str, *, days: int = 30) -> SignInStats | None:
        if not cookie or not self._enabled:
            return None

        records = self._fetch_credit_records(cookie)
        amounts = self._extract_sign_in_amounts(records, days)
        count = len(amounts)
        if count == 0:
            return None

        total = round(sum(amounts), 2)
        average = round(total / count, 2)
        return SignInStats(
            total_amount=total,
            average=average,
            days_count=count,
            period=f"Last {days} days",
        )

    def _fetch_credit_records(self, cookie: str) -> list[Sequence[object]]:
        headers = {"Cookie": cookie}
        records: list[Sequence[object]] = []

        with self._http_client.open_session() as session:
            for page in range(1, self.MAX_PAGES + 1):
                if page > 1:
                    time.sleep(self.REQUEST_DELAY_SECONDS)

                page_records = self._fetch_credit_page(session, page, headers)
                if not page_records:
                    break

                records.extend(page_records)

        return records

    def _fetch_credit_page(
        self,
        session: HttpSession,
        page: int,
        headers: dict[str, str],
    ) -> list[Sequence[object]]:
        response = session.request(
            "GET",
            f"https://www.nodeseek.com/api/account/credit/page-{page}",
            headers=headers,
            timeout=10,
        )
        data = self._response_json(response)
        if data is None or not data.get("success"):
            return []

        raw_records = data.get("data")
        if not isinstance(raw_records, list):
            return []

        records: list[Sequence[object]] = []
        for record in raw_records:
            if isinstance(record, (list, tuple)):
                records.append(record)
        return records

    @staticmethod
    def _response_json(response: HttpResponse) -> dict[str, object] | None:
        try:
            data = response.json()
        except (json.JSONDecodeError, ValueError):
            return None
        if not isinstance(data, dict):
            return None
        return data

    def _extract_sign_in_amounts(self, records: list[Sequence[object]], days: int) -> list[float]:
        amounts: list[float] = []
        for record in records:
            if len(record) < 3 or "签到收益" not in str(record[2]):
                continue

            amount = self._to_float(record[0])
            if amount is None:
                continue

            amounts.append(amount)
            if len(amounts) >= days:
                break

        return amounts

    @staticmethod
    def _to_float(value: object) -> float | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(str(value))
        except ValueError:
            return None
