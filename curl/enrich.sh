#!/usr/bin/env bash
# Screen a crypto address for AML/KYT risk with PublicAML. No API key required.
set -euo pipefail

ADDRESS="${1:-0x08723392ed15743cc38513c4925f5e6be5c17243}"
CHAIN="${2:-ETH}"

curl -sS -X POST 'https://intelapi.publicaml.org/v1/enrich' \
  -H 'Content-Type: application/json' \
  -d "{
    \"addresses\": [{ \"wallet_address\": \"${ADDRESS}\", \"chain\": \"${CHAIN}\" }],
    \"include\": [\"aml_score\", \"category\"]
  }"
