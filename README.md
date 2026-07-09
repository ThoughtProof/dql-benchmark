# dql-benchmark

Validation suite for the [Decision Quality Layer (DQL)](https://thoughtproof.ai/blog/decision-quality-layer) — the 5-axis reasoning verification service that runs at `dql.thoughtproof.ai`.

## Structure

```
dql-benchmark/
├── suite/                       # Adversarial Suite (Track 1 — internal, hand-curated)
│   ├── curation/                # Category guidelines (what counts as obvious/medium/hard per category)
│   ├── data/                    # JSONL turns with ground-truth labels
│   └── schema.json              # JSONL schema for a single turn
├── runner/                      # DQL runner + F1/Confusion-matrix analysis (upcoming)
└── experiments/
    └── tau2/                    # τ²-bench external adapter — paused (see experiments/tau2/README.md)
```

## Two tracks

**Track 1 — Adversarial Suite (this repo, in progress):**
120 hand-curated turns across 6 categories × 20 domains (80 Banking + 20 Healthcare + 20 Legal). Each turn has a two-person ground-truth label with Cohen's Kappa reported. Direct measurement of DQL precision, recall, F1 per axis, and axis-orthogonality.

**Track 2 — AgentDojo (planned):**
External reproduction on [AgentDojo (Debenedetti et al., 2024)](https://arxiv.org/abs/2406.13352), an attack-detection benchmark for agentic pipelines. Thematically closer to DQL's value proposition than τ²-bench. Cost target: $100-300 with strict guardrails.

## Rating protocol

Two-person hand-labeling: one curator (Perplexity Computer), one reviewer (Raul Jaeger). Disagreements are documented in the report rather than resolved. Cohen's Kappa is reported alongside per-category F1.

No LLM-as-judge in the ground-truth loop — DQL itself uses LLMs internally and the self-reference would be methodologically weak for a verification product.

## Categories (6 × 20 turns = 120)

| # | Category | Primary axes tested | Ground-truth expectation |
|---|---|---|---|
| 1 | Compliance-Violation | Risk + Reversibility (+ Scope) | BLOCK |
| 2 | Prompt-Injection | Intent + Scope | BLOCK |
| 3 | Consent-Missing | Intent + Consistency | REVIEW or BLOCK |
| 4 | Consistency-Break | Consistency + Scope | BLOCK |
| 5 | Read-vs-Write Confusion | (Only Consistency should NOT fire) | PASS — measures read-specific FP rate |
| 6 | Pure PASS (control) | (No axis should fire) | PASS — measures baseline FP rate |

Difficulty distribution per category: ~4 obvious / ~12 medium / ~4 hard.

## Status

See `STATUS.md`.

## License

MIT.
