"""MCP tools backed by the local Agentpass browser harness."""

from __future__ import annotations

import os
import re
from urllib.parse import quote_plus

from mcp.server.mcpserver import MCPServer
from mcp_types import ToolAnnotations
from patchright.async_api import TimeoutError as PatchrightTimeoutError

from .browser import launch
from .heal import guard


server = MCPServer(
    "agentpass",
    version="0.2.0",
    instructions=(
        "Use search before add_to_cart so the user can choose an exact product. "
        "Treat add_to_cart and checkout as write actions requiring confirmation. "
        "checkout only prepares Amazon's final review page and never places an order."
    ),
)


def _money(raw: str) -> float | None:
    match = re.search(r"(?:US\$|\$)?\s*([0-9][0-9,]*(?:\.[0-9]{2})?)", raw)
    return float(match.group(1).replace(",", "")) if match else None


def _valid_asin(asin: str) -> str:
    normalized = asin.strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{10}", normalized):
        raise ValueError("asin must contain exactly 10 letters or digits")
    return normalized


async def _search(query: str) -> list[dict]:
    context = await launch()
    try:
        page = context.pages[0]
        await page.goto(
            f"https://www.amazon.com/s?k={quote_plus(query)}",
            wait_until="domcontentloaded",
        )
        await guard(page)

        results: list[dict] = []
        cards = page.locator('div[data-component-type="s-search-result"][data-asin]')
        try:
            await cards.first.wait_for(state="attached", timeout=10_000)
        except PatchrightTimeoutError:
            # A second guard captures late-rendered challenge pages and gives the
            # caller a useful MCP error instead of a misleading empty catalog.
            await guard(page)
            raise RuntimeError(
                "Amazon did not return search results. Inspect block.png, wait, "
                "and retry with the signed-in Agentpass profile."
            )
        for index in range(min(await cards.count(), 12)):
            card = cards.nth(index)
            asin = (await card.get_attribute("data-asin") or "").strip()
            title_node = card.locator("h2 span").first
            price_node = card.locator(".a-price .a-offscreen").first
            if not asin or await title_node.count() == 0:
                continue
            title = (await title_node.inner_text()).strip()
            price = None
            if await price_node.count():
                price = (await price_node.inner_text()).strip()
            results.append({"title": title, "asin": asin, "price": price})
        return results
    finally:
        await context.close()


@server.tool(
    title="Search Amazon products",
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=True,
    ),
)
async def search(query: str) -> list[dict]:
    """Use this to find Amazon products before choosing one to add to the cart."""
    if not query.strip():
        raise ValueError("query cannot be empty")
    return await _search(query.strip())


@server.tool(
    title="Add an Amazon product to cart",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
)
async def add_to_cart(asin: str, qty: int = 1) -> dict:
    """Use this only after the user chooses an exact ASIN and quantity."""
    normalized = _valid_asin(asin)
    if not 1 <= qty <= 30:
        raise ValueError("qty must be between 1 and 30")

    context = await launch()
    try:
        page = context.pages[0]
        await page.goto(
            f"https://www.amazon.com/dp/{normalized}",
            wait_until="domcontentloaded",
        )
        challenged = await guard(page)
        if challenged and "Robot or human" in await page.title():
            return {"ok": False, "asin": normalized, "qty": qty, "status": "challenge"}

        quantity = page.locator("#quantity")
        if qty != 1 and await quantity.count():
            await quantity.select_option(str(qty))
        button = page.locator("#add-to-cart-button")
        if await button.count() == 0:
            return {"ok": False, "asin": normalized, "qty": qty, "status": "unavailable"}
        await button.click()
        await page.wait_for_load_state("domcontentloaded")
        return {"ok": True, "asin": normalized, "qty": qty, "status": "added"}
    finally:
        await context.close()


@server.tool(
    title="Prepare Amazon checkout",
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=True,
    ),
)
async def checkout(confirm_under: float) -> dict:
    """Open checkout when the cart subtotal is under a caller-provided ceiling.

    This prepares the checkout page but never clicks the final order-placement
    control; a person must review and confirm the resulting order.
    """
    if confirm_under <= 0:
        raise ValueError("confirm_under must be positive")

    context = await launch()
    try:
        page = context.pages[0]
        await page.goto(
            "https://www.amazon.com/gp/cart/view.html",
            wait_until="domcontentloaded",
        )
        await guard(page)
        subtotal_node = page.locator(
            ".sc-subtotal .a-offscreen, #sc-subtotal-amount-activecart .a-offscreen"
        ).first
        if await subtotal_node.count() == 0:
            return {"ok": False, "status": "empty_or_signed_out"}

        subtotal_text = (await subtotal_node.inner_text()).strip()
        subtotal = _money(subtotal_text)
        if subtotal is None:
            return {"ok": False, "status": "unknown_total", "subtotal": subtotal_text}
        if subtotal > confirm_under:
            return {
                "ok": False,
                "status": "over_limit",
                "subtotal": subtotal,
                "confirm_under": confirm_under,
            }

        proceed = page.locator(
            "input[name='proceedToRetailCheckout'], #sc-buy-box-ptc-button input"
        ).first
        if await proceed.count() == 0:
            return {"ok": False, "status": "checkout_unavailable", "subtotal": subtotal}
        await proceed.click()
        await page.wait_for_load_state("domcontentloaded")
        await guard(page)
        return {
            "ok": True,
            "status": "ready_for_human_confirmation",
            "subtotal": subtotal,
            "url": page.url,
        }
    finally:
        await context.close()


def main() -> None:
    """Run the Agentpass MCP server over stdio."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
