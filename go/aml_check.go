// Screen a crypto address for AML/KYT risk with PublicAML. No API key required.
// Docs: https://publicaml.org/api
//   go run aml_check.go 0x08723392ed15743cc38513c4925f5e6be5c17243 ETH
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
)

const enrichURL = "https://intelapi.publicaml.org/v1/enrich"

type Entity struct {
	WalletAddress string   `json:"wallet_address"`
	Chain         string   `json:"chain"`
	AMLScore      float64  `json:"aml_score"`
	Category      string   `json:"category"`
	Sanctioned    bool     `json:"sanctioned"`
}

// AMLCheck returns the enriched entity for one address.
func AMLCheck(address, chain string) (Entity, error) {
	body, _ := json.Marshal(map[string]any{
		"addresses": []map[string]string{{"wallet_address": address, "chain": chain}},
		"include":   []string{"aml_score", "category"},
	})
	resp, err := http.Post(enrichURL, "application/json", bytes.NewReader(body))
	if err != nil {
		return Entity{}, err
	}
	defer resp.Body.Close()
	var out struct {
		Entities []Entity `json:"entities"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&out); err != nil {
		return Entity{}, err
	}
	if len(out.Entities) == 0 {
		return Entity{}, fmt.Errorf("no entity returned")
	}
	return out.Entities[0], nil
}

// IsRisky reports whether the address is sanctioned or at/above threshold.
func IsRisky(address, chain string, threshold float64) (bool, error) {
	e, err := AMLCheck(address, chain)
	if err != nil {
		return false, err
	}
	return e.Sanctioned || e.AMLScore >= threshold, nil
}

func main() {
	addr := "0x08723392ed15743cc38513c4925f5e6be5c17243"
	chain := "ETH"
	if len(os.Args) > 1 {
		addr = os.Args[1]
	}
	if len(os.Args) > 2 {
		chain = os.Args[2]
	}
	e, err := AMLCheck(addr, chain)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
	fmt.Printf("aml_score=%.1f category=%s sanctioned=%v\n", e.AMLScore, e.Category, e.Sanctioned)
	risky, _ := IsRisky(addr, chain, 75)
	if risky {
		fmt.Println("RISKY — block the transfer")
	} else {
		fmt.Println("OK")
	}
}
