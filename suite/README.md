# DQL Adversarial Suite

120 hand-curated turns for measuring DQL precision, recall, F1 per axis, and axis orthogonality.

## Structure

- `schema.json` — JSON Schema for a single turn (`suite/data/*.jsonl` conforms to this)
- `curation/` — one guideline per category: what counts as obvious/medium/hard, example templates
- `data/` — the JSONL files (one per category, 20 turns each)

## Curation workflow

1. **Curator** (Perplexity Computer) writes a turn following the guideline in `curation/NN_<category>.md`.
2. Turn goes into `data/NN_<category>.jsonl` with `review_status: "pending"`.
3. **Reviewer** (Raul) reads through, marks `agree` / `agree_with_diff_axes` / `disagree` and adds `reviewer_notes` if needed.
4. Cohen's Kappa is computed once all 120 turns are reviewed. Report threshold: **κ ≥ 0.7 = publishable**.
5. Disagreements are documented in the final report, not resolved. Transparency > false consensus.

## Category-to-axis map

| Category | Should fire | Should NOT fire | Difficulty split (obvious/medium/hard) |
|---|---|---|---|
| compliance_violation | risk, reversibility, often scope | — | 4 / 12 / 4 |
| prompt_injection | intent, scope | — | 4 / 12 / 4 |
| consent_missing | intent, consistency | — | 4 / 12 / 4 |
| consistency_break | consistency, scope | — | 4 / 12 / 4 |
| read_vs_write | — | risk, reversibility, scope | 4 / 12 / 4 (all should PASS) |
| pure_pass | — | intent, scope, risk, consistency, reversibility | 4 / 12 / 4 (all should PASS) |

## Domain balance

| Domain | Count | Coverage |
|---|---|---|
| banking | 80 | Categories 1-6, ~13-14 each |
| healthcare | 20 | Categories 1-6, ~3-4 each |
| legal | 20 | Categories 1-6, ~3-4 each |

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
- **Cohen's Kappa** on the two-person labeling

## No LLM-as-judge in the ground-truth loop

DQL uses LLMs internally. Using an LLM as a rater would create a self-reference weakness ("of course an LLM agreed with our LLM's output"). Two-person hand-labeling with Kappa is the methodologically defensible choice for a verification product.
