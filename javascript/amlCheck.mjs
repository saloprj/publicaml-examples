// Screen a crypto address for AML/KYT risk with PublicAML. No API key required.
// Node 18+ (global fetch).  Docs: https://publicaml.org/api
//   node amlCheck.mjs 0x08723392ed15743cc38513c4925f5e6be5c17243 ETH

const ENRICH_URL = 'https://intelapi.publicaml.org/v1/enrich'

export async function amlCheck(address, chain = 'ETH') {
  const res = await fetch(ENRICH_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      addresses: [{ wallet_address: address, chain }],
      include: ['aml_score', 'category'],
    }),
  })
  if (!res.ok) throw new Error(`enrich failed: ${res.status}`)
  const { entities } = await res.json()
  return entities[0]
}

export async function isRisky(address, chain = 'ETH', threshold = 75) {
  const e = await amlCheck(address, chain)
  return Boolean(e.sanctioned) || (e.aml_score ?? 0) >= threshold
}

// Pre-transaction gate: throw before you sign / accept funds.
export async function assertClean(address, chain = 'ETH') {
  const e = await amlCheck(address, chain)
  if (e.sanctioned || (e.aml_score ?? 0) >= 75) {
    throw new Error(`High AML risk (${e.category}) — transfer blocked`)
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const addr = process.argv[2] || '0x08723392ed15743cc38513c4925f5e6be5c17243'
  const chain = process.argv[3] || 'ETH'
  const e = await amlCheck(addr, chain)
  console.log(`aml_score=${e.aml_score} category=${e.category} sanctioned=${e.sanctioned}`)
  console.log((await isRisky(addr, chain)) ? 'RISKY — block the transfer' : 'OK')
}
