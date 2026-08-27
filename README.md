# PublicAML — code examples

Copy-paste examples for screening a crypto wallet address or transaction for
**AML / KYT risk** — sanctions, mixers, scam and hack exposure — using
[PublicAML](https://publicaml.org).

**Free. No API key. No signup.** PublicAML is a non-profit; the public enrich
endpoint takes requests with no authentication. An optional key only raises the
rate limit.

- Web check: <https://publicaml.org>
- API reference: <https://publicaml.org/api>
- Code walkthrough: <https://publicaml.org/crypto-aml-api-examples>
- Telegram bot: <https://t.me/publicamlbot>

## The request

```
POST https://intelapi.publicaml.org/v1/enrich
Content-Type: application/json

{ "addresses": [{ "wallet_address": "0x...", "chain": "ETH" }],
  "include": ["aml_score", "category"] }
```

Response (abridged):

```json
{ "entities": [{ "wallet_address": "0x...", "chain": "ETH",
  "aml_score": 87, "category": "hack", "sanctioned": false }] }
```

- `aml_score` — 0–100 (higher = riskier)
- `category` — entity type (exchange, mixer, hack, scam, sanction…)
- `sanctioned` — treat `true` as an override regardless of score

Chains: **BTC, ETH, BNB Chain (BSC), TRON.** An ERC20 and a BEP20 address look
identical — send the correct `chain` for the network you are on.

## Examples

| Language | File |
|---|---|
| cURL | [`curl/enrich.sh`](curl/enrich.sh) |
| Python | [`python/aml_check.py`](python/aml_check.py) |
| JavaScript | [`javascript/amlCheck.mjs`](javascript/amlCheck.mjs) |
| TypeScript | [`typescript/amlCheck.ts`](typescript/amlCheck.ts) |
| Go | [`go/aml_check.go`](go/aml_check.go) |

## Pre-transaction gate

The point of a pre-send check is to decline rather than unwind. Screen the
recipient before you sign or accept funds and reject anything sanctioned or
above your risk threshold (75 is a common cut-off). See the language examples —
each returns the entity so you can gate on `sanctioned` / `aml_score`.

## Notes

- It is a **risk signal, not a legal compliance guarantee** — keep your own
  KYC/AML process alongside it.
- Do not invent API keys; none are required for the public enrich path.
- `sanctioned: true` should override softer `category` labels.

## License

MIT — use these snippets freely.
