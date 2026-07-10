# Reproducibility Manifest — PR #3 Re-Run (consistency-fix)

**Report:** [`runs/report_pr3_rerun.md`](../report_pr3_rerun.md)
**Raw data:** [`runs/results_pr3.jsonl`](../results_pr3.jsonl)
**Commit (decision-quality-layer, branch head at test time):** `7f167dd` on branch `fix/consistency-axis-non-sequitur-calibration`

## Artifact integrity

| Artifact | Path | Size | SHA256 |
|---|---|---:|---|
| Raw results (100 rows) | `runs/results_pr3.jsonl` | see below | `c08934f5df2380d8b832e348e5a1e5027610fdb8766586c3db7a909faa79b52a` |

Verify locally:

```bash
git clone https://github.com/ThoughtProof/dql-benchmark
cd dql-benchmark
sha256sum runs/results_pr3.jsonl
# expect: c08934f5df2380d8b832e348e5a1e5027610fdb8766586c3db7a909faa79b52a
```

## Sanity re-computation (from raw JSONL)

Reproduces every headline number in the report from `results_pr3.jsonl` alone.

| Metric | Value from raw | Report claims |
|---|---:|---:|
| Rows | 100 | 100 |
| Strict | 67/100 | 67/100 ✅ |
| Relaxed | 85/100 | 85/100 ✅ |
| DQL verdict split | see raw | – |
| Axis FAIL fires — consistency | 47 | 47 ✅ |
| Axis FAIL fires — risk | 64 | 64 ✅ |
| Axis FAIL fires — scope | 52 | 52 ✅ |
| Axis FAIL fires — intent | 51 | 51 ✅ |
| Axis FAIL fires — reversibility | 52 | 52 ✅ |
| Fetch-failed axes | 1/500 | 1/500 ✅ |

Per-category strict (P/R/B):

| Category | Strict | P/R/B |
|---|---:|---|
| compliance_violation | 15/17 | 0/0/17 |
| prompt_injection | 16/17 | 0/2/15 |
| consent_missing | 8/17 | 0/1/16 |
| consistency_break | 14/17 | 0/0/17 |
| read_vs_write | 6/16 | 6/9/1 |
| **pure_pass** | **8/16** | **8/8/0** |

## Runtime environment

- Node 20.20.1
- Cascade: in-process `PotCliCascade` (imported directly from `/tmp/dql-src/dist/` — no HTTP roundtrip)
- LLM: OpenServ `inference-api.openserv.ai` via `serv-nano` + `serv-swift`
- Retry wrapper: `RetryLlmClient` — attempts=6, exp backoff, retryable patterns: `429`, `proxy`, `fetch failed`
- Workers: 2 (initial) + 1 (retry pass on 19 fetch-failed turns)
- Resume support: skips rows already in output that have no fetch-failed axes
- Wall time: initial 857.9s + retry 233.1s = 1091s

## Runner + fix workflow

1. Checkout branch `fix/consistency-axis-non-sequitur-calibration`
2. `npm run typecheck && npm test` → 73/73 green
3. `npm run build`
4. Live smoke (5 curated cases — 3 target Cat-6 + 2 real non-sequiturs): `scripts/consistency-fix-smoke.mjs`
5. Full suite: `scripts/run-adversarial-suite.mjs --workers 2 --out runs/adversarial-pr3.jsonl`
6. Retry fetch-failed rows: prune failed rows from output, re-run same script with `--workers 1` (resume-support picks up remaining 19)
7. Copy to `dql-benchmark/runs/results_pr3.jsonl`, generate report + manifest, commit + push

## Data quality notes

- 1 axis-result remains fetch-failed (0.2 %). No turn is blocked or misclassified by fetch-failed alone.
- Two Cat-6 turns (adv_090, adv_094) show consistency=UNCERTAIN@0.86 rather than PASS — thin reasoning triggered UNCERTAIN under the new stricter STEP-1 gate. This is not a regression (no FAIL, no BLOCK) but a minor calibration edge worth noting for v0.4.
