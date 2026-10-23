from __future__ import annotations

import os

import pytest

from agentpass.mcp import _search


pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.getenv("AGENTPASS_RUN_AMAZON") != "1",
        reason="set AGENTPASS_RUN_AMAZON=1 to run the live storefront check",
    ),
]


@pytest.mark.asyncio
async def test_amazon_search_returns_structured_products(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("AGENTPASS_PROFILE", str(tmp_path / "profile"))
    results = await _search("usb cable")

    assert results
    assert {"title", "asin", "price"} <= results[0].keys()
    assert len(results[0]["asin"]) == 10
