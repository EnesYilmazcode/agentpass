"""Natural-looking pointer, keyboard, and scroll primitives."""

from __future__ import annotations

import math
import random
from typing import Any


async def human_move(page: Any, x: float, y: float) -> None:
    """Move the pointer along a cubic Bézier curve instead of teleporting."""
    start_x = max(0.0, x * random.uniform(0.05, 0.25))
    start_y = max(0.0, y * random.uniform(0.05, 0.25))
    control_1 = (start_x + (x - start_x) * 0.35, start_y + random.uniform(-80, 80))
    control_2 = (start_x + (x - start_x) * 0.70, y + random.uniform(-80, 80))
    steps = max(12, min(40, int(math.hypot(x - start_x, y - start_y) / 20)))

    await page.mouse.move(start_x, start_y)
    for step in range(1, steps + 1):
        t = step / steps
        inverse = 1 - t
        next_x = (
            inverse**3 * start_x
            + 3 * inverse**2 * t * control_1[0]
            + 3 * inverse * t**2 * control_2[0]
            + t**3 * x
        )
        next_y = (
            inverse**3 * start_y
            + 3 * inverse**2 * t * control_1[1]
            + 3 * inverse * t**2 * control_2[1]
            + t**3 * y
        )
        await page.mouse.move(next_x, next_y)
        await page.wait_for_timeout(random.uniform(4, 12))


async def human_type(page: Any, text: str) -> None:
    """Type text one key at a time with variable latency."""
    for character in text:
        delay = random.uniform(35, 125)
        await page.keyboard.type(character, delay=delay)


async def human_scroll(page: Any, px: float) -> None:
    """Scroll by ``px`` using an eased multi-step curve."""
    if px == 0:
        return

    steps = max(8, min(30, int(abs(px) / 60)))
    previous = 0.0
    for step in range(1, steps + 1):
        t = step / steps
        eased = 1 - (1 - t) ** 3
        target = px * eased
        delta = target - previous
        previous = target
        await page.mouse.wheel(0, delta)
        await page.wait_for_timeout(random.uniform(8, 20))

