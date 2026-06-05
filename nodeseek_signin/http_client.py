from __future__ import annotations

from collections.abc import Mapping
from types import TracebackType
from typing import Callable, Literal, Protocol

from niquests import Response, Session


HttpMethod = Literal["GET", "POST"]
JsonBody = dict[str, object] | list[object] | None
SessionFactory = Callable[..., Session]
ProxySpec = dict[str, str]


class HttpResponse(Protocol):
    status_code: int
    text: str

    def json(self) -> object:
        ...


class HttpSession:
    def __init__(
        self,
        session: Session,
        *,
        default_timeout: int,
        proxies: ProxySpec | None,
    ) -> None:
        self._session = session
        self._default_timeout = default_timeout
        self._proxies = proxies

    def __enter__(self) -> HttpSession:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._session.close()

    def request(
        self,
        method: HttpMethod,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
        json_body: JsonBody = None,
    ) -> Response:
        request_timeout = self._default_timeout if timeout is None else timeout
        request_headers = dict(headers) if headers is not None else None

        if method == "GET":
            return self._session.get(
                url,
                headers=request_headers,
                timeout=request_timeout,
                proxies=self._proxies,
            )
        return self._session.post(
            url,
            headers=request_headers,
            timeout=request_timeout,
            json=json_body,
            proxies=self._proxies,
        )


class NodeSeekHttpClient:
    def __init__(
        self,
        *,
        proxy_url: str,
        timeout: int,
        session_factory: SessionFactory | None = None,
    ) -> None:
        self._proxy_url = proxy_url
        self._timeout = timeout
        self._session_factory = session_factory or Session

    def open_session(self) -> HttpSession:
        session = self._session_factory(timeout=self._timeout)
        return HttpSession(
            session,
            default_timeout=self._timeout,
            proxies=self._proxy_spec(),
        )

    def request(
        self,
        method: HttpMethod,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: int | None = None,
        json_body: JsonBody = None,
    ) -> Response:
        with self.open_session() as session:
            return session.request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout,
                json_body=json_body,
            )

    def _proxy_spec(self) -> ProxySpec | None:
        if not self._proxy_url:
            return None
        return {
            "http": self._proxy_url,
            "https": self._proxy_url,
        }
