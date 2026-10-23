# agentpass

A local Patchright harness that gives an AI agent a browser consistent with the
user's installed Chrome, then leaves room for standards-based agent identity.

## Rules — read before acting

1. Pick sensible defaults and ship working code.
2. Working code over prose.
3. Commit after every passing test using conventional commits.
4. Ground truth:
   - Headless Chromium can expose `HeadlessChrome` in Client Hints and
     `navigator.userAgentData.brands`.
   - `extra_http_headers` does not change `navigator.userAgentData`; CDP
     `Network.setUserAgentOverride` with `userAgentMetadata` does.
   - This project changes browser identity values only; it does not proxy traffic.

## Build order

Implement in this order, gated on tests:
`fingerprint.py` → `browser.py` → `heal.py` → `humanize.py` → `mcp.py`.

## Self-test targets

- https://tls.peet.ws/api/all
- https://bot.sannysoft.com
- https://arh.antoinevastel.com/bots/areyouheadless

## Hard constraints

- Use Patchright: `from patchright.async_api import async_playwright`.
- Use `channel="chrome"`, `headless=False`, and `launch_persistent_context`.
- Never commit a user-data directory; `.profile/` belongs in `.gitignore`.

