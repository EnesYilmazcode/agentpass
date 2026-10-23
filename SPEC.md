# SPEC

## `agentpass/fingerprint.py`

`chrome_headers(version: str = "141") -> dict[str, str]`

Return desktop Chrome headers: `user-agent`, `sec-ch-ua`,
`sec-ch-ua-mobile`, `sec-ch-ua-platform`, `accept`, and `accept-language`.
No return value may contain `Headless`.

## `agentpass/browser.py`

`async launch(profile: str | None = None) -> BrowserContext`

- Patchright with Chrome, headed mode, and a persistent context.
- Profile resolution: argument, then `AGENTPASS_PROFILE`, then `./.profile`.
- Apply `chrome_headers()` as extra HTTP headers.
- Apply a CDP `Network.setUserAgentOverride` including `userAgentMetadata`.
- Launch with `--disable-blink-features=AutomationControlled`.
- Return the context; the caller closes it.

## `agentpass/heal.py`

`BLOCK_MARKERS: list[str]`

`async guard(page) -> bool`

Detect a challenge page. When detected, save `block.png`, reload, and wait two
seconds. Required markers: `unauthorized AI agent`, `Conditions of Use`, and
`Robot or human?`.

## `agentpass/humanize.py`

- `async human_move(page, x, y)` uses a Bézier path.
- `async human_type(page, text)` uses variable per-key delay.
- `async human_scroll(page, px)` uses eased, multi-step scrolling.

No third-party dependency is required beyond the browser library.

## `agentpass/mcp.py`

Expose these MCP tools over the shared browser harness:

- `search(query: str) -> list[dict]`
- `add_to_cart(asin: str, qty: int = 1) -> dict`
- `checkout(confirm_under: float) -> dict`

Each tool launches and closes its own browser and invokes `guard()` before
interacting. Checkout must stop before final order placement and report the
order total for explicit confirmation.

