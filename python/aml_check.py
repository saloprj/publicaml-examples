"""Screen a crypto address for AML/KYT risk with PublicAML.

Free, keyless API — no signup. Docs: https://publicaml.org/api
    pip install requests
    python aml_check.py 0x08723392ed15743cc38513c4925f5e6be5c17243 ETH
"""
import sys
import requests

ENRICH_URL = "https://intelapi.publicaml.org/v1/enrich"


def aml_check(address: str, chain: str = "ETH") -> dict:
    """Return the enriched entity for one address (aml_score, category, ...)."""
    resp = requests.post(
        ENRICH_URL,
        json={
            "addresses": [{"wallet_address": address, "chain": chain}],
            "include": ["aml_score", "category"],
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["entities"][0]


def is_risky(address: str, chain: str = "ETH", threshold: int = 75) -> bool:
    """True if the address is sanctioned or scores at/above the threshold."""
    e = aml_check(address, chain)
    return bool(e.get("sanctioned")) or (e.get("aml_score") or 0) >= threshold


if __name__ == "__main__":
    addr = sys.argv[1] if len(sys.argv) > 1 else "0x08723392ed15743cc38513c4925f5e6be5c17243"
    chain = sys.argv[2] if len(sys.argv) > 2 else "ETH"
    entity = aml_check(addr, chain)
    print(f"aml_score={entity.get('aml_score')} "
          f"category={entity.get('category')} "
          f"sanctioned={entity.get('sanctioned')}")
    print("RISKY — block the transfer" if is_risky(addr, chain) else "OK")
