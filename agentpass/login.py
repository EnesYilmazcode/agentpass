"""Interactive Amazon sign-in bootstrap for the persistent Agentpass profile."""

from __future__ import annotations

import asyncio

from .browser import launch


async def login() -> None:
    """Open Amazon so the user can authenticate without sharing credentials."""
    context = await launch()
    try:
        page = context.pages[0]
        await page.goto("https://www.amazon.com/", wait_until="domcontentloaded")
        print("Chrome is open with the Agentpass profile.")
        print("Sign in to Amazon yourself, then return here.")
        await asyncio.to_thread(input, "Press Enter after Amazon shows your account: ")
    finally:
        await context.close()


def main() -> None:
    asyncio.run(login())


if __name__ == "__main__":
    main()
