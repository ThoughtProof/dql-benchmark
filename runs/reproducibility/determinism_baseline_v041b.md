# Reproducibility Manifest — Determinismus-Baseline v0.4.1b

- **File:** `runs/determinism_baseline_v041b.jsonl`
- **SHA256:** `df152bb44e5aef192cc5edb3e7b4905dca4fcce10869bdc0021d146f870ce557`
- **Rows:** 100 (adv_001–adv_100)
- **Draws pro Case:** 5
- **Source repo:** ThoughtProof/decision-quality-layer @ commit `1af3692` (main after PR #6 merge)
- **Runner:** `scripts/run-determinism-metric.mjs` (branch `feat/determinism-metric`)
- **Cascade backend:** `pot-cli` mit serv-swift via inference-api.openserv.ai
- **Datum:** 2026-07-10

## Key metrics
- aggregate_stable: 94/100 (94.0%)
- any_axis_flip: 21/100 (21.0%)
- rows_with_errors: 0/100

## Reproduce
```bash
git clone https://github.com/ThoughtProof/decision-quality-layer && cd decision-quality-layer
git checkout 1af3692
npm ci && npm run build
DQL_CASCADE=pot-cli SERV_API_KEY=<key> \
  node --require ./node-proxy-bootstrap.cjs \
  scripts/run-determinism-metric.mjs \
  --dir scenarios/adversarial --draws 5 --workers 1 \
  --out runs/determinism_baseline_v041b.jsonl
sha256sum runs/determinism_baseline_v041b.jsonl
# Expected SHA256: df152bb44e5aef192cc5edb3e7b4905dca4fcce10869bdc0021d146f870ce557 (up to LLM sampling variance — draws are non-deterministic)
```
Note: draws are LLM-sampled → verbatim byte-repro not possible; metrics ±2 rows within N=5 noise band.
