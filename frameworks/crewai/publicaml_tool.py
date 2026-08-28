"""PublicAML tool for CrewAI — screen a crypto address for AML / KYT risk.

Free and keyless (PublicAML is a non-profit). Give this tool to a CrewAI agent
so it can check a wallet address for sanctions, mixer, scam or hack exposure.

    pip install crewai crewai-tools requests

Example:

    from crewai import Agent
    from publicaml_tool import PublicAMLTool

    analyst = Agent(
        role="Compliance analyst",
        goal="Screen counterparties before payment",
        backstory="Checks every address for AML risk.",
        tools=[PublicAMLTool()],
    )
"""

from __future__ import annotations

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

ENRICH_URL = "https://intelapi.publicaml.org/v1/enrich"
SUPPORTED_CHAINS = ("BTC", "ETH", "BSC", "TRON")


class PublicAMLInput(BaseModel):
    address: str = Field(..., description="The crypto wallet address to screen.")
    chain: str = Field(..., description="Chain: BTC, ETH, BSC or TRON.")


class PublicAMLTool(BaseTool):
    name: str = "publicaml_screen_address"
    description: str = (
        "Screen a single crypto wallet address for AML / KYT risk via PublicAML. "
        "Returns a risk score (0-100), risk level and the category the address is "
        "linked to (exchange, mixer, scam, hack, sanction, ...). Chains: BTC, ETH, "
        "BSC, TRON. A 'sanction' category is blocking on its own; an address with no "
        "data is reported as NOT FOUND and must not be treated as clean."
    )
    args_schema: type[BaseModel] = PublicAMLInput

    def _run(self, address: str, chain: str) -> str:
        chain = (chain or "").upper()
        if chain not in SUPPORTED_CHAINS:
            return f"invalid_chain: '{chain}'. Use one of {', '.join(SUPPORTED_CHAINS)}."
        try:
            resp = requests.post(
                ENRICH_URL,
                json={
                    "addresses": [{"wallet_address": address, "chain": chain}],
                    "include": ["aml_score", "category"],
                },
                timeout=30,
            )
        except requests.RequestException as exc:
            return f"error: could not reach PublicAML ({exc})."

        if resp.status_code >= 400:
            try:
                err = resp.json()
                return (
                    f"error: {err.get('error', resp.status_code)} — "
                    f"{err.get('detail', resp.text[:200])}. {err.get('hint', '')}".strip()
                )
            except ValueError:
                return f"error: HTTP {resp.status_code}."

        entities = (resp.json() or {}).get("entities") or []
        if not entities:
            return (
                f"{address} ({chain}): NOT FOUND — no data. Do not treat as clean."
            )

        e = entities[0]
        note = " sanctions exposure is blocking regardless of score." if e.get("category") == "sanction" else ""
        return (
            f"{address} ({chain}): aml_score={e.get('aml_score')}, "
            f"risk_level={e.get('risk_level') or 'UNKNOWN'}, "
            f"category={e.get('category') or 'unlabeled'}.{note}"
        )
