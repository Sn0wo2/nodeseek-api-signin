from __future__ import annotations

import json
import random
import time

from niquests.exceptions import RequestException

from nodeseek_signin.cookies import merge_response_cookies
from nodeseek_signin.http_client import HttpResponse, NodeSeekHttpClient
from nodeseek_signin.models import SignInResult


class HttpSignInService:
    def __init__(self, http_client: NodeSeekHttpClient, *, random_mode: bool) -> None:
        self._http_client = http_client
        self._random_mode = random_mode

    def sign_in(self, cookie: str) -> SignInResult:
        try:
            if self._random_mode:
                time.sleep(random.uniform(1, 3))

            response = self._http_client.request(
                "POST",
                self._attendance_url(),
                headers=self.get_headers(cookie),
                json_body={},
            )
            result = self._classify_attendance_response(response)
            if result.success:
                updated_cookie = merge_response_cookies(cookie, response)
                if updated_cookie != cookie:
                    result.updated_cookie = updated_cookie
            return result
        except RequestException as exc:
            return SignInResult(False, f"HTTP sign-in exception: {exc}", "http")

    @staticmethod
    def get_headers(cookie: str) -> dict[str, str]:
        return {
            "Cache-Control": "no-cache",
            "Cookie": cookie,
            "Origin": "https://www.nodeseek.com",
            "Referer": "https://www.nodeseek.com/board",
            "X-Requested-With": "XMLHttpRequest",
        }

    def _attendance_url(self) -> str:
        random_value = "true" if self._random_mode else "false"
        return f"https://www.nodeseek.com/api/attendance?random={random_value}"

    @staticmethod
    def _classify_attendance_response(response: HttpResponse) -> SignInResult:
        status = response.status_code

        match status:
            case 200:
                result = HttpSignInService._response_json(response)
                if result is None:
                    return SignInResult(
                        False,
                        f"Response parse failed: {response.text[:100]}",
                        "http",
                    )

                if result.get("success"):
                    return SignInResult(
                        True,
                        f"Sign-in success! Today +{result.get('gain', 0)} drumsticks, "
                        f"total {result.get('current', 0)}",
                        "http",
                    )
                message = result.get("message")
                return SignInResult(
                    False,
                    "Sign-in failed" if message is None else str(message),
                    "http",
                )

            case 500:
                result = HttpSignInService._response_json(response)
                if result is None:
                    return SignInResult(False, "Server 500 error", "http")

                message = str(result.get("message", ""))

                if any(keyword in message for keyword in ("已完成签到", "已签到", "重复操作")):
                    return SignInResult(True, f"Already signed in: {message}", "http")
                return SignInResult(False, f"Server error: {message}", "http")

            case 401:
                return SignInResult(
                    False,
                    "Cookie expired, please update manually",
                    "http",
                    cookie_expired=True,
                )
            case 403:
                return SignInResult(
                    False,
                    "403 Forbidden - possibly blocked by Cloudflare",
                    "http",
                )
            case 302:
                return SignInResult(
                    False,
                    "302 redirect - cookie likely expired",
                    "http",
                    cookie_expired=True,
                )
            case _:
                body = response.text.lower()
                if any(keyword in body for keyword in ("login", "signin", "sign in", "登录")):
                    return SignInResult(
                        False,
                        f"HTTP {status} - cookie likely expired",
                        "http",
                        cookie_expired=True,
                    )
                return SignInResult(False, f"HTTP {status} error", "http")

    @staticmethod
    def _response_json(response: HttpResponse) -> dict[str, object] | None:
        try:
            result = response.json()
        except (json.JSONDecodeError, ValueError):
            return None
        if not isinstance(result, dict):
            return None
        return result
