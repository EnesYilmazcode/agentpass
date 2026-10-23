from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from agentpass.heal import BLOCK_MARKERS, guard


FIXTURES = Path(__file__).parent / "fixtures"


def test_required_block_markers_are_present() -> None:
    assert {"unauthorized AI agent", "Conditions of Use", "Robot or human?"} <= set(
        BLOCK_MARKERS
    )


@pytest.mark.asyncio
async def test_guard_recovers_from_fixture_challenge(monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(tmp_path)
    page = AsyncMock()
    page.content.return_value = (FIXTURES / "blocked.html").read_text(encoding="utf-8")

    assert await guard(page) is True
    page.screenshot.assert_awaited_once_with(
        path=str(tmp_path / "block.png"), full_page=True
    )
    page.reload.assert_awaited_once_with(wait_until="domcontentloaded")
    page.wait_for_timeout.assert_awaited_once_with(2_000)


@pytest.mark.asyncio
async def test_guard_leaves_normal_page_untouched() -> None:
    page = AsyncMock()
    page.content.return_value = (FIXTURES / "normal.html").read_text(encoding="utf-8")

    assert await guard(page) is False
    page.screenshot.assert_not_awaited()
    page.reload.assert_not_awaited()
