"""Small recovery guard for recognizable browser challenge pages."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol


BLOCK_MARKERS: list[str] = [
    "unauthorized AI agent",
    "Conditions of Use",
    "Robot or human?",
]


class GuardedPage(Protocol):
    async def content(self) -> str: ...

    async def screenshot(self, **kwargs: object) -> bytes: ...

    async def reload(self, **kwargs: object) -> object: ...

    async def wait_for_timeout(self, timeout: float) -> None: ...


async def guard(page: GuardedPage) -> bool:
    """Capture and retry a page when a known challenge marker is present."""
    html = await page.content()
    folded = html.casefold()
    blocked = any(marker.casefold() in folded for marker in BLOCK_MARKERS)
    if not blocked:
        return False

    await page.screenshot(path=str(Path.cwd() / "block.png"), full_page=True)
    await page.reload(wait_until="domcontentloaded")
    await page.wait_for_timeout(2_000)
    return True

