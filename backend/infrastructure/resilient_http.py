"""
================================================================================
TradeMindAI: Hardened Upstream Market-Data Client (REL-01)
================================================================================
Provides connection pooling, bounded retries, exponential backoff with jitter,
explicit timeouts, and protection against retrying non-idempotent operations.
================================================================================
"""

import asyncio
import random
import time
from typing import Any

import httpx


class UpstreamUnavailable(Exception):
    pass


class ResilientHTTPClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 5.0,
        max_attempts: int = 3,
        max_connections: int = 50,
    ):
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        self.max_attempts = max_attempts
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout_seconds),
            limits=httpx.Limits(
                max_connections=max_connections,
                max_keepalive_connections=min(20, max_connections),
            ),
            follow_redirects=False,
            trust_env=False,
        )

    async def get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        last_error: Exception | None = None

        for attempt in range(self.max_attempts):
            try:
                response = await self.client.get(
                    path,
                    params=params,
                )

                if response.status_code not in {
                    429, 500, 502, 503, 504
                }:
                    response.raise_for_status()
                    return response

                last_error = httpx.HTTPStatusError(
                    "Transient upstream failure",
                    request=response.request,
                    response=response,
                )

            except (
                httpx.TimeoutException,
                httpx.TransportError,
            ) as exc:
                last_error = exc

            if attempt + 1 < self.max_attempts:
                delay = min(
                    0.25 * (2 ** attempt),
                    2.0,
                )
                await asyncio.sleep(
                    random.uniform(0, delay)
                )

        raise UpstreamUnavailable(
            "Market-data provider unavailable"
        ) from last_error

    async def close(self) -> None:
        await self.client.aclose()
