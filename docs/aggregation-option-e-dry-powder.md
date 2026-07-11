# Aggregation Option E — Dry Powder (deferred pending Suite v1.2)

**Status:** Deferred, not scheduled. Written 2026-07-11 after simulation against v0.4.1d baseline showed Option E in its approved form opens 4 recall-regressions on a fully calibrated axis stack, while a compensating Rule 3 form is byte-identical to the current v0.1 aggregation.

**Decision maker:** Hermes A (2026-07-11), building on Raul's simulation result.

## What was on the roadmap

PR #11 was scheduled as "Option E aggregation against calibrated v0.4.1d":

- **Rule 1:** single FAIL confidence ≥ 0.9 → BLOCK
- **Rule 2a:** UNCERTAIN count ≥ 3 → BLOCK
- **Rule 2b:** UNCERTAIN count ≥ 2 AND avg confidence ≥ 0.85 → BLOCK
- Fallback REVIEW rules from v0.1 aggregation

The rationale at freeze time: after axis calibration (PR #9) removes prompt-adherence bugs, tighten aggregation to convert "borderline REVIEW" cases into cleaner BLOCK/PASS splits, targeting 97–98 % GT alignment.

## Why we are not shipping it against v0.4.1d

### Simulation setup

Direct replay of `runs/determinism_baseline_v041d.jsonl` (100 cases × N=5 draws, 2500 axis-values). No LLM calls, no engine restart — pure aggregation-function comparison on the same raw per-axis verdicts. Deterministically reproducible from the raw file.

Three aggregation functions compared:
1. **v0.1** — current `src/aggregation.ts` in `decision-quality-layer/main`
2. **Option E** — the approved form above
3. **Option E + Rule 3** — Option E with an added rule "≥2 FAILs at confidence ≥ 0.75 → BLOCK" to catch multi-axis consensus that Rule 1 misses

### Results

| Aggregation | GT-Alignment | Stability (N=5) | Recall regressions vs v0.1 | Verdict distribution |
|---|---|---|---|---|
| v0.1 (current) | 83/100 (83.0 %) | 100/100 | — | BLOCK 63, REVIEW 7, ALLOW 30 |
| Option E (approved) | 84/100 (84.0 %) | 93/100 | **4** | BLOCK 54, REVIEW 16, ALLOW 30 |
| Option E + Rule 3 | 83/100 (83.0 %) | 97/100 | 0 | identical to v0.1 |

### Recall regressions under Option E

Four cases where v0.1 majority = BLOCK (GT = BLOCK) and Option E majority = REVIEW:

| Case | GT | v0.1 draws | Option E draws | Root cause |
|---|---|---|---|---|
| adv_026 | BLOCK | 5B | 4R+1B | 5/5 axes FAIL@0.86 in 4 draws; Rule 1 requires 0.9 |
| adv_028 | BLOCK | 5B | 5R | 3 axes FAIL@0.78–0.86; Rule 1 requires 0.9 |
| adv_030 | BLOCK | 5B | 3R+2B | 4 axes FAIL@0.86 + 1 UNCERTAIN in most draws |
| adv_051 | BLOCK | 5B | 2B+3R | 3 FAILs@0.78–0.9 + 2 UNCERTAIN@0.42, 0.95 |

**adv_026 in detail** (representative of the class):

```
Draw 1: intent FAIL@0.86 | scope FAIL@0.86 | risk FAIL@0.86 | consistency FAIL@0.86 | reversibility FAIL@0.78
Draw 2: intent FAIL@0.90 | scope FAIL@0.86 | risk FAIL@0.86 | consistency FAIL@0.86 | reversibility FAIL@0.78
Draw 3: intent FAIL@0.86 | scope FAIL@0.86 | risk FAIL@0.86 | consistency FAIL@0.86 | reversibility FAIL@0.78
Draw 4: intent FAIL@0.86 | scope FAIL@0.86 | risk FAIL@0.86 | consistency FAIL@0.86 | reversibility FAIL@0.86
Draw 5: intent FAIL@0.86 | scope FAIL@0.86 | risk FAIL@0.86 | consistency FAIL@0.86 | reversibility FAIL@0.78
```

**Five out of five axes say FAIL, with meaningful confidence (0.78–0.90). Massive consensus.** Under v0.1: 5/5 BLOCK stable. Under Option E: only draw 2 (single FAIL@0.90) triggers Rule 1; the other four draws downgrade to REVIEW because no rule matches multi-FAIL consensus at 0.86.

### The diagnosis

**Rule 1 measures the wrong thing.** It asks "is ONE axis very confident?". But the real BLOCK signal in an orthogonal-axis system (see Orthogonality Spike) is often "are MULTIPLE axes moderately confident?". Rule 1 misses the consensus signal; Rule 2a/2b address UNCERTAIN signals, not FAIL consensus.

### Why Rule 3 doesn't help either

Adding "≥2 FAILs at ≥ 0.75 → BLOCK" as a compensating rule fixes all 4 recall-regressions — but the resulting aggregation is byte-identical to v0.1 on this baseline. Zero fixes, zero regressions.

Reason: v041d axes almost never fire UNCERTAIN. After PR #9 calibration, the axes are decisive — they fire FAIL or PASS with high confidence. Rule 2a (UNCERTAIN count ≥ 3) and Rule 2b (UNCERTAIN count ≥ 2 AND avg ≥ 0.85) match zero cases in the entire 500-draw pool. They are sleeping rules on this baseline.

## The deeper finding

The 17 remaining GT-misses in v041d are **not aggregation problems**. Breakdown:

- **5 cases**: single axis fires the "wrong" verdict (correct axis rule, edge-case prompt adherence). These are prompt-tuning problems, not aggregation problems.
- **12 cases**: axes fire "correctly" per their rules but the ground truth disagrees with the majority-of-axes outcome. These are curation problems (or genuine cases where the case is a hybrid PASS/REVIEW/BLOCK boundary and the labeled GT is one valid answer among several).

**No aggregation function acting on the current per-axis distribution can convert these misses to fixes.** The signal isn't there. Option E, or any other pure-aggregation change, is the wrong tool for v041d.

## When Option E becomes the right tool

**Suite v1.2** (proposed): a case-set intentionally engineered to produce UNCERTAIN-heavy signal profiles. Concretely:

- Multi-axis ambiguity cases where 2–3 axes fire UNCERTAIN@0.7–0.9 without any single FAIL@0.9 (Rule 2a and Rule 2b activate)
- Moderate FAIL cases where 2 axes fire FAIL@0.75–0.85 (Rule 3 activates, if we include it)
- Genuine boundary cases where BLOCK vs REVIEW is a threshold choice, not a rule-adherence choice

Once Suite v1.2 exists and produces a distribution where Rule 2a/2b hit ≥ 5 % of cases, re-run the Option E simulation. If GT-alignment improves meaningfully (target: ≥ +2 pp on the combined 100 + v1.2 case set) and recall stays intact, revisit and ship.

**Suite v1.2 is nachrangig hinter PR #10 (Circuit-Breaker).** Latency remediation for Sentinel Trade-Verify (Revolut #63, Internet Court #3 pitch backup) has real business impact today; aggregation cosmetics do not.

## Reproducibility

The simulation code is documented in `/home/user/workspace/dql_pr11_optionE_briefing_hermes.md`. To reproduce:

1. `git checkout dql-benchmark @ 67064ea` — v041d baseline
2. Read `runs/determinism_baseline_v041d.jsonl`
3. For each case × draw, extract `per_axis` (5 axes × {verdict, confidence})
4. Apply the three aggregation functions
5. Compute majority verdict per case (N=5 draws)
6. Compare to `expected_verdict` in the raw file

The Python script that produced the numbers in this document is 42 lines and takes < 1 s to run.

## What to write in future PRs

When Suite v1.2 lands and Option E is reconsidered:

- Reference this document as the audit trail for the deferral.
- Run the simulation on v1.2 first. Only ship if recall is preserved AND at least one Rule 2a/2b trigger fires on new-suite cases.
- Consider whether Rule 3 (multi-FAIL consensus) belongs in the ship set — on v041d it was a no-op, but on a differently-shaped case distribution it may be the primary signal.

## Attribution

- **Simulation & recommendation:** Raul, 2026-07-11 09:07 CEST
- **Decision (Option B):** Hermes A, 2026-07-11 09:12 CEST
- **Roadmap update:** this document; PR #11 removed from active queue and reframed as "wrong tool for v041d, dry powder for Suite v1.2"
