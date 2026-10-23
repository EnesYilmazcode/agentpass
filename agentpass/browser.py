"""Persistent Chrome launcher with coherent HTTP and JavaScript identity values."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, Coroutine

from patchright.async_api import BrowserContext, Page, async_playwright

from .fingerprint import chrome_headers


def _profile_path(profile: str | None) -> Path:
    configured = profile or os.getenv("AGENTPASS_PROFILE") or ".profile"
    return Path(configured).expanduser().resolve()


def _user_agent_metadata(version: str) -> dict[str, Any]:
    major = version.split(".", 1)[0]
    return {
        "brands": [
            {"brand": "Chromium", "version": major},
            {"brand": "Google Chrome", "version": major},
            {"brand": "Not?A_Brand", "version": "24"},
        ],
        "fullVersionList": [
            {"brand": "Chromium", "version": f"{major}.0.0.0"},
            {"brand": "Google Chrome", "version": f"{major}.0.0.0"},
            {"brand": "Not?A_Brand", "version": "24.0.0.0"},
        ],
        "fullVersion": f"{major}.0.0.0",
        "platform": "Windows",
        "platformVersion": "10.0.0",
        "architecture": "x86",
        "model": "",
        "mobile": False,
        "bitness": "64",
        "wow64": False,
    }


async def _apply_cdp_identity(page: Page, version: str) -> None:
    headers = chrome_headers(version)
    session = await page.context.new_cdp_session(page)
    await session.send("Network.enable")
    await session.send(
        "Network.setUserAgentOverride",
        {
            "userAgent": headers["user-agent"],
            "acceptLanguage": headers["accept-language"],
            "platform": "Windows",
            "userAgentMetadata": _user_agent_metadata(version),
        },
    )


async def launch(profile: str | None = None) -> BrowserContext:
    """Launch headed Chrome with a persistent local profile."""
    version = os.getenv("AGENTPASS_CHROME_VERSION", "141")
    headers = chrome_headers(version)
    profile_path = _profile_path(profile)
    profile_path.mkdir(parents=True, exist_ok=True)

    playwright = await async_playwright().start()
    try:
        context = await playwright.chromium.launch_persistent_context(
            str(profile_path),
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            extra_http_headers=headers,
        )
    except BaseException:
        await playwright.stop()
        raise

    # A persistent context starts with one page. Install the override before the
    # caller navigates it, and repeat it for every subsequently opened target.
    for page in context.pages:
        await _apply_cdp_identity(page, version)
    context.on("page", lambda page: _apply_cdp_identity(page, version))

    original_close: Callable[..., Coroutine[Any, Any, None]] = context.close

    async def close_and_stop(*args: Any, **kwargs: Any) -> None:
        try:
            await original_close(*args, **kwargs)
        finally:
            await playwright.stop()

    # Patchright's BrowserContext is a regular Python wrapper, so preserving its
    # concrete type while extending close() keeps ownership intuitive for callers.
    context.close = close_and_stop  # type: ignore[method-assign]
    return context
