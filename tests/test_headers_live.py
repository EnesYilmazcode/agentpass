from __future__ import annotations

import pytest

from agentpass.browser import launch


@pytest.mark.live
@pytest.mark.asyncio
async def test_javascript_client_hints_do_not_claim_headless(tmp_path) -> None:
    context = await launch(str(tmp_path / "profile"))
    try:
        page = context.pages[0]
        await page.goto("https://example.com", wait_until="domcontentloaded")
        brands = await page.evaluate(
            "() => navigator.userAgentData.brands.map(b => b.brand).join(',')"
        )

        assert "HeadlessChrome" not in brands
        assert "Chrome" in brands
    finally:
        await context.close()
