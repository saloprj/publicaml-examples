"""PublicAML tool for LangChain — screen a crypto address for AML / KYT risk.

Free and keyless (PublicAML is a non-profit). Drop this tool into any LangChain
agent so it can check whether a wallet address is tied to sanctions, mixers,
scams or hacks before acting on it.

    pip install langchain-core requests

Example:

    from langchain_core.messages import HumanMessage
    from langchain.agents import create_react_agent   # or any agent
    from publicaml_tool import PublicAMLTool

    tools = [PublicAMLTool()]
    # ... hand `tools` to your agent / LLM with tool-calling ...

Or call it directly:

    print(PublicAMLTool().invoke({"address": "0x28c6c06298d514db089934071355e5743bf21d60",
                                  "chain": "ETH"}))
"""

from __future__ import annotations

import requests
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

ENRICH_URL = "https://intelapi.publicaml.org/v1/enrich"
SUPPORTED_CHAINS = ("BTC", "ETH", "BSC", "TRON")


class PublicAMLInput(BaseModel):
    address: str = Field(description="The crypto wallet address to screen.")
    chain: str = Field(
        description="Chain the address belongs to: BTC, ETH, BSC or TRON. "
        "The same 0x address is a different wallet on ETH, BSC and TRON, so pass "
        "the right one."
    )


class PublicAMLTool(BaseTool):
    """LangChain tool that screens a crypto address for AML/KYT risk via PublicAML."""

    name: str = "publicaml_screen_address"
    description: str = (
        "Screen a single crypto wallet address for AML / KYT risk. Returns a risk "
        "score (0-100), a risk level (LOW/MEDIUM/HIGH/CRITICAL) and the category the "
        "address is linked to (exchange, mixer, gambling, bridge, scam, hack, "
        "sanction, ...). Chains: BTC, ETH, BSC, TRON. A 'sanction' category is a "
        "blocking fact on its own. An address with no data is reported as NOT FOUND "
        "and must not be treated as clean."
    )
    args_schema: type[BaseModel] = PublicAMLInput

    def _run(self, address: str, chain: str) -> str:
        chain = (chain or "").upper()
        if chain not in SUPPORTED_CHAINS:
            return (
                f"invalid_chain: '{chain}'. Supported chains are "
                f"{', '.join(SUPPORTED_CHAINS)}."
            )
        try:
            resp = requests.post(
                ENRICH_URL,
                json={
                    "addresses": [{"wallet_address": address, "chain": chain}],
                    "include": ["aml_score", "category"],
                },
                timeout=30,
            )
        except requests.RequestException as exc:  # network error
            return f"error: could not reach PublicAML ({exc})."

        if resp.status_code >= 400:
            # The API returns a self-correcting error, e.g. invalid_address_format.
            try:
                err = resp.json()
                return (
                    f"error: {err.get('error', resp.status_code)} — "
                    f"{err.get('detail', resp.text[:200])}. "
                    f"{err.get('hint', '')}".strip()
                )
            except ValueError:
                return f"error: HTTP {resp.status_code}."

        entities = (resp.json() or {}).get("entities") or []
        if not entities:
            return (
                f"{address} ({chain}): NOT FOUND — no data for this address. "
                "Do not treat this as clean; it only means it is not in the dataset."
            )

        e = entities[0]
        score = e.get("aml_score")
        risk = e.get("risk_level") or "UNKNOWN"
        category = e.get("category") or "unlabeled"
        note = ""
        if category == "sanction":
            note = " sanctions exposure is a blocking fact regardless of score."
        return (
            f"{address} ({chain}): aml_score={score}, risk_level={risk}, "
            f"category={category}.{note}"
        )


if __name__ == "__main__":
    tool = PublicAMLTool()
    # A known exchange wallet (low risk) and a sanctions-exposed address.
    for addr in (
        "0x28c6c06298d514db089934071355e5743bf21d60",
        "0x8589427373D6D84E98730D7795D8f6f8731FDA16",
    ):
        print(tool.invoke({"address": addr, "chain": "ETH"}))
