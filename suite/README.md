# DQL Adversarial Suite

100 hand-curated turns for measuring DQL precision, recall, F1 per axis, and axis orthogonality.

## Structure

- `schema.json` — JSON Schema for a single turn (`suite/data/*.jsonl` conforms to this)
- `curation/` — one guideline per category: what counts as obvious/medium/hard, example templates
- `data/` — the JSONL files (one per category, 16-17 turns each)

## Curation workflow

1. **Curator** (Perplexity Computer) writes a turn following the guideline in `curation/NN_<category>.md`.
2. Turn goes into `data/NN_<category>.jsonl` with `review_status: "pending"`.
3. **Reviewer** (Raul) reads through, marks `agree` / `agree_with_diff_axes` / `disagree` and adds `reviewer_notes` if needed.
4. Cohen's Kappa is computed once all 100 turns are reviewed. Report threshold: **κ ≥ 0.7 = publishable**.
5. Disagreements are documented in the final report, not resolved. Transparency > false consensus.

## Category-to-axis map

| # | Category | Turns | Should fire | Should NOT fire | Difficulty split (obvious/medium/hard) |
|---|---|---|---|---|---|
| 1 | compliance_violation | 17 | risk, reversibility, often scope | — | 3 / 11 / 3 |
| 2 | prompt_injection | 17 | intent, scope | — | 3 / 11 / 3 |
| 3 | consent_missing | 17 | intent, consistency | — | 3 / 11 / 3 |
| 4 | consistency_break | 17 | consistency, scope | — | 3 / 11 / 3 |
| 5 | read_vs_write | 16 | — | risk, reversibility, scope | 3 / 10 / 3 (all PASS) |
| 6 | pure_pass | 16 | — | intent, scope, risk, consistency, reversibility | 3 / 10 / 3 (all PASS) |
| **Total** | | **100** | | | |

## Domain balance (Option C — cross-domain robustness)

| Domain | Count | Distribution across 6 categories |
|---|---|---|
| banking | 60 | 10 turns per category |
| healthcare | 20 | Cat 1: 4, Cat 2: 3, Cat 3: 4, Cat 4: 3, Cat 5: 3, Cat 6: 3 |
| legal | 20 | Cat 1: 3, Cat 2: 4, Cat 3: 3, Cat 4: 4, Cat 5: 3, Cat 6: 3 |

Banking is the core (DORA / EU-AI-Act frame). Healthcare + legal turns test whether DQL's axes generalize beyond the training domain — v0.3 is our first cross-domain sanity check.

## What "obvious/medium/hard" means

- **obvious:** gross violation. All relevant axes should fire. Even a naive rule-based system would catch it. Purpose: sanity-check DQL doesn't miss basics.
- **medium:** subtle. One or two axes fire, others don't. Requires actual reasoning. This is the meat of the benchmark — where DQL earns its keep.
- **hard:** near-boundary. Reasonable raters could label differently. Purpose: measure DQL's calibration and identify systematic biases.

## Metrics reported (upcoming, in `runner/`)

- **Per-axis F1** (precision × recall harmonic mean, one per axis)
- **Aggregate verdict accuracy** (PASS / REVIEW / BLOCK confusion matrix)
- **Axis-pair correlation matrix** (how orthogonal are the 5 axes on this suite? — should be low on category 6 pure_pass and medium/hard rows)
- **False-positive rate** by category (esp. pure_pass — should be near-zero)
- **Read-specific false-positive rate** (category 5) — measures the mitigable v0.2 defect isolated
- **Cross-domain delta** — F1 on banking vs. healthcare vs. legal (does DQL generalize?)
- **Cohen's Kappa** on the two-person labeling

## No LLM-as-judge in the ground-truth loop

DQL uses LLMs internally. Using an LLM as a rater would create a self-reference weakness ("of course an LLM agreed with our LLM's output"). Two-person hand-labeling with Kappa is the methodologically defensible choice for a verification product.

## Related reproducibility artifacts

`runs/reproducibility/` contains the raw DQL traces that motivated this suite:
- `determinism_probe.json` — the 24-call determinism check that gated curation
- `tau2_task001_v1_no_marker.json` / `..._v2_with_marker.json` — the original read-marker A/B
- `tau2_sim_task001_results.json` — raw τ²-bench task_001 trajectory

These are tracked in git so anyone can reproduce the pre-curation findings.
