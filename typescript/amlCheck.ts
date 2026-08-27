// Screen a crypto address for AML/KYT risk with PublicAML. No API key required.
// Docs: https://publicaml.org/api

const ENRICH_URL = 'https://intelapi.publicaml.org/v1/enrich'

export type Chain = 'BTC' | 'ETH' | 'BSC' | 'TRON'

export interface AmlEntity {
  wallet_address: string
  chain: string
  aml_score?: number
  category?: string
  sanctioned?: boolean
}

export async function amlCheck(address: string, chain: Chain = 'ETH'): Promise<AmlEntity> {
  const res = await fetch(ENRICH_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      addresses: [{ wallet_address: address, chain }],
      include: ['aml_score', 'category'],
    }),
  })
  if (!res.ok) throw new Error(`enrich failed: ${res.status}`)
  const data = (await res.json()) as { entities: AmlEntity[] }
  return data.entities[0]
}

export async function isRisky(address: string, chain: Chain = 'ETH', threshold = 75): Promise<boolean> {
  const e = await amlCheck(address, chain)
  return Boolean(e.sanctioned) || (e.aml_score ?? 0) >= threshold
}

// Pre-transaction gate.
export async function assertClean(address: string, chain: Chain = 'ETH'): Promise<void> {
  const e = await amlCheck(address, chain)
  if (e.sanctioned || (e.aml_score ?? 0) >= 75) {
    throw new Error(`High AML risk (${e.category}) — transfer blocked`)
  }
}
