# agentpass

> A passport for AI agents on the open web.

Your agent opens Chrome. The site sees Chrome. The JavaScript runtime agrees.
Then the agent can identify itself on its own terms.

That sounds obvious. It is not.

Setting request headers alone leaves a split identity: the network says Chrome
while `navigator.userAgentData` can say something else. Agentpass keeps the HTTP
headers and browser Client Hints aligned through Chrome DevTools Protocol, using
your local Chrome and a persistent profile.

No proxy fleet. No remote browser. One small Python harness.

## What ships

- A headed, persistent Patchright + Chrome context.
- Coherent Chrome headers and `navigator.userAgentData` brands.
- Local profile reuse via `AGENTPASS_PROFILE`.
- Bézier mouse movement, variable typing cadence, and eased scrolling.
- Challenge detection with a local `block.png` diagnostic.
- MCP tools for product search, cart updates, and checkout preparation.
- A hard stop before final order placement.

## Start

```bash
git clone <your-repo-url> agentpass
cd agentpass
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[test]"
pytest -v
```

Run the MCP server over stdio:

```bash
agentpass
```

Sign in once using the dedicated local profile. Agentpass never receives or
stores your password; authentication happens in the Chrome window:

```powershell
agentpass-login
```

Choose a reusable Chrome profile:

```bash
export AGENTPASS_PROFILE="$PWD/.profile"
```

PowerShell:

```powershell
$env:AGENTPASS_PROFILE = "$PWD\.profile"
```

## The proof

The test that matters checks the JavaScript surface, not just request headers:

```python
brands = await page.evaluate(
    "() => navigator.userAgentData.brands.map(b => b.brand).join(',')"
)
assert "HeadlessChrome" not in brands
assert "Chrome" in brands
```

Run the live fingerprint checks:

```bash
pytest -v tests/test_fingerprint_live.py tests/test_headers_live.py
```

The Amazon search smoke test is opt-in because it touches a live storefront:

```bash
AGENTPASS_RUN_AMAZON=1 pytest -v tests/test_amazon_live.py
```

## API

```python
from agentpass.browser import launch

context = await launch()
page = context.pages[0]
await page.goto("https://example.com")
# use the page
await context.close()
```

Three MCP tools sit on top: `search(query)`, `add_to_cart(asin, qty)`, and
`checkout(confirm_under)`. Each owns its browser lifecycle. Checkout validates
the cart subtotal and opens the review flow, but never places the order.

## Connect to ChatGPT privately

Agentpass supports OpenAI's Secure MCP Tunnel over its stdio transport. The
tunnel is outbound-only, so the browser profile and MCP server remain on your
computer.

Prerequisites:

1. In OpenAI Platform, create a tunnel associated with your personal Platform
   organization and target ChatGPT workspace.
2. Create a restricted runtime API key whose principal has **Tunnels Read +
   Use**. Do not use an admin key for the running client.
3. Install OpenAI's current `tunnel-client` at
   `%LOCALAPPDATA%\agentpass\bin\tunnel-client.exe`.

Configure the local profile without writing the API key into the repository:

```powershell
.\scripts\setup-tunnel.ps1 -TunnelId "tunnel_REPLACE_ME"
.\scripts\run-tunnel.ps1
```

Both scripts prompt for the runtime key without echoing it and keep it only in
the current process environment.

Keep that PowerShell window running. In ChatGPT on the web, open **Plugins**,
select **Add custom MCP server**, choose **Tunnel**, select the same tunnel,
create the private plugin, and install it. Leave confirmation enabled for
`add_to_cart` and `checkout`; `search` is advertised as read-only.

Try this prompt:

> Use Agentpass to find three well-reviewed bags of roasted chestnuts under
> $20. Show me the choices. After I choose one, add one bag to my cart and
> prepare checkout, but do not place the order.

## Why now

The open web needs a cleaner contract for agents: behave like a browser at the
transport layer, identify as an agent at the protocol layer, and let sites make
an informed decision. Agentpass is the local, inspectable harness for that
contract.

MIT licensed. Bring your own Chrome.
