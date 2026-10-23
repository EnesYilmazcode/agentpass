from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from agentpass.humanize import human_move, human_scroll, human_type


def fake_page() -> SimpleNamespace:
    return SimpleNamespace(
        mouse=SimpleNamespace(move=AsyncMock(), wheel=AsyncMock()),
        keyboard=SimpleNamespace(type=AsyncMock()),
        wait_for_timeout=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_human_move_uses_a_multi_step_path_and_lands_on_target() -> None:
    page = fake_page()

    await human_move(page, 400, 240)

    assert page.mouse.move.await_count > 10
    final = page.mouse.move.await_args_list[-1].args
    assert final == pytest.approx((400, 240))


@pytest.mark.asyncio
async def test_human_type_sends_characters_with_variable_delays(monkeypatch) -> None:
    page = fake_page()
    delays = iter([40.0, 75.0, 110.0])
    monkeypatch.setattr("agentpass.humanize.random.uniform", lambda *_: next(delays))

    await human_type(page, "abc")

    calls = page.keyboard.type.await_args_list
    assert [call.args[0] for call in calls] == ["a", "b", "c"]
    assert [call.kwargs["delay"] for call in calls] == [40.0, 75.0, 110.0]


@pytest.mark.asyncio
async def test_human_scroll_is_eased_and_totals_requested_distance() -> None:
    page = fake_page()

    await human_scroll(page, 600)

    calls = page.mouse.wheel.await_args_list
    assert len(calls) >= 8
    assert sum(call.args[1] for call in calls) == pytest.approx(600)
    assert calls[0].args[1] != pytest.approx(calls[-1].args[1])
