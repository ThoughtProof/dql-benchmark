# dql-tau2-eval

External validation of the [Decision Quality Layer (DQL)](https://github.com/ThoughtProof/decision-quality-layer) against [τ²-bench](https://github.com/sierra-research/tau2-bench) (Sierra Research, June 2025).

**Status:** in progress. Track A of DQL v0.3.

## What this is

DQL is a five-axis reasoning watchdog: it looks at an agent's next-step reasoning and fires up to five independent axes (intent, scope, risk, consistency, reversibility) when the step looks off. See the [DQL Spike-80 baseline](https://github.com/ThoughtProof/decision-quality-layer/blob/main/docs/SPIKE-RESULTS.md) for the internal regression numbers.

The internal Spike-80 set is DQL-authored. This repo answers the fair-play question: **does DQL do anything useful on external, non-DQL agent traces?**

We take τ²-bench (Sierra's tool-agent-user benchmark, banking domain) and run the same agent three ways:

| Track | Description | Question answered |
|---|---|---|
| **A — Baseline** | Sonnet-4 solves τ²-banking tasks, no DQL | τ²-benchmark reference |
| **B1 — Observer** | Same agent, DQL sees each reasoning step, agent does not | Do DQL axes correlate with task failure on external traces? |
| **B2 — Retry** | Same agent, when DQL fires ≥2 axes, agent gets axes back as feedback and retries the step (max 1 retry/turn) | Does DQL as an in-loop watchdog raise Pass^k reliability? |

## Method

- **Benchmark:** τ²-bench, `banking_knowledge` domain, full test split (97 tasks)
- **Agent model:** `claude-sonnet-5` (single model — this is a DQL effect study, not a model comparison)
- **User simulator:** `claude-sonnet-5` (τ² default, same model both sides)
- **Provider route:** OpenServ (`inference-api.openserv.ai/v1`) — same infrastructure as DQL v0.2 production
- **Retrieval config:** `bm25_grep` (self-contained, no embeddings or sandbox; keeps DQL effect measurement clean)
- **DQL endpoint:** `https://dql.thoughtproof.ai/dql/verify` (production DQL v0.2, cascade `pot-cli`)
- **Trials:** 4 per task (τ² Pass^k metric)
- **Determinism:** temperature 0, seed 42 (Sentinel-congruent)

## Repo layout

```
dql_tau2_eval/
├── adapter.py           # DQL client — POST /dql/verify per agent step
├── tracks/
│   ├── baseline.py      # Track A wrapper
│   ├── observer.py      # Track B1 wrapper
│   └── retry.py         # Track B2 wrapper
├── analysis/
│   ├── passk.py         # Pass^1/^2/^3/^4 per track
│   ├── fp_tp.py         # DQL false-positive / true-positive rates
│   └── report.py        # Publication-ready markdown output
└── runs/                # per-run traces + reports (gitignored except summaries)
```

## Running

```bash
# 1. Install (Python 3.11)
pip install -e .

# 2. Env
export ANTHROPIC_API_KEY=...
export DQL_URL=https://dql.thoughtproof.ai
# no DQL API key needed — v0.2 is dev-open

# 3. Smoke test (5 tasks, 1 trial, baseline only, ~$1-3)
dql-tau2 smoke

# 4. Pilot (10 tasks, 1 trial, all 3 tracks, ~$5-15)
dql-tau2 pilot

# 5. Full run (test split, 4 trials, all 3 tracks, ~$300-500, 6-10h)
dql-tau2 full
```

## Results

Populated after full run in `runs/full-YYYY-MM-DD/report.md`.

## References

- [DQL Spike-80 baseline](https://github.com/ThoughtProof/decision-quality-layer/blob/main/docs/SPIKE-RESULTS.md)
- [τ²-bench paper (Sierra, 2025)](https://github.com/sierra-research/tau2-bench)
- [ADR-0008 — why not BrowseSafe](https://github.com/ThoughtProof/decision-quality-layer/blob/main/docs/adr/ADR-0008-reject-browsesafe-cross-benchmark.md)

## License

MIT.
