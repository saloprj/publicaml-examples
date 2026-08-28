# PublicAML in AI agent frameworks

Give an AI agent the ability to screen a crypto wallet address for **AML / KYT
risk** — sanctions, mixers, scam and hack exposure — using [PublicAML](https://publicaml.org).
Free, keyless, chains BTC / ETH / BSC / TRON.

## Zero code: MCP server (Claude Desktop, Cursor, any MCP client)

The fastest option — no code, works in any MCP-compatible client:

```json
{
  "mcpServers": {
    "publicaml": {
      "command": "npx",
      "args": ["-y", "@publicaml/mcp-server"]
    }
  }
}
```

Tools: `screen_address`, `trace_funds`, `list_counterparties`.
Package: <https://www.npmjs.com/package/@publicaml/mcp-server>

## LangChain

[`langchain/publicaml_tool.py`](langchain/publicaml_tool.py) — a `PublicAMLTool`
(`langchain_core.tools.BaseTool`) you can hand to any LangChain agent.

```python
from publicaml_tool import PublicAMLTool
tools = [PublicAMLTool()]
```

## CrewAI

[`crewai/publicaml_tool.py`](crewai/publicaml_tool.py) — a `PublicAMLTool`
(`crewai.tools.BaseTool`).

```python
from publicaml_tool import PublicAMLTool
analyst = Agent(role="Compliance analyst", tools=[PublicAMLTool()], ...)
```

## What the tool returns

For each address: `aml_score` (0–100), `risk_level` (LOW/MEDIUM/HIGH/CRITICAL)
and `category` (exchange, mixer, gambling, bridge, scam, hack, sanction, …).

Read it the agent-safe way: a `sanction` category is a blocking fact on its own,
independent of the score; an address with **no data** is reported as `NOT FOUND`
and must not be presented as clean.

No API key is required. An optional key only raises the rate limit —
see <https://publicaml.org/api>.
