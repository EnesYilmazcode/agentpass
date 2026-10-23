from __future__ import annotations

import pytest

from agentpass.mcp import _money, _valid_asin, server


def test_money_parser() -> None:
    assert _money("$1,234.56") == 1234.56
    assert _money("US$ 9.99") == 9.99
    assert _money("not available") is None


def test_asin_validation() -> None:
    assert _valid_asin("b08n5wrwnw") == "B08N5WRWNW"
    with pytest.raises(ValueError):
        _valid_asin("../bad")


@pytest.mark.asyncio
async def test_mcp_exposes_expected_tools() -> None:
    tools = await server.list_tools()
    assert {tool.name for tool in tools} == {"search", "add_to_cart", "checkout"}

