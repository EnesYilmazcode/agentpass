from __future__ import annotations

import pytest

from agentpass.browser import launch


@pytest.mark.live
@pytest.mark.asyncio
async def test_network_fingerprint_has_expected_chrome_values(tmp_path) -> None:
    context = await launch(str(tmp_path / "profile"))
    try:
        page = context.pages[0]
        await page.goto("https://tls.peet.ws/api/all", wait_until="domcontentloaded")
        payload = await page.locator("body").inner_text()

        assert "HeadlessChrome" not in payload
        assert "Google Chrome" in payload
        assert "sec-ch-ua" in payload.lower()
    finally:
        await context.close()

