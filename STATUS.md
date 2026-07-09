# Sprint Status — DQL v0.3 Benchmarking

**Sprint start:** 2026-07-09 evening
**Current phase:** Track 1 (Adversarial Suite) — curation freigegeben nach Determinismus-Probe
**Repo:** [ThoughtProof/dql-benchmark](https://github.com/ThoughtProof/dql-benchmark) (renaming from dql-tau2-eval pending)

## Strategic pivot on 2026-07-09 ~20:00 CEST

Original plan was τ²-bench external validation on `banking_knowledge`. Paused after task_001 due to cost blow-up on task_002 (agent kb_search runaway, 300 Sonnet-5 requests in 240s via OpenServ, ~$35 for the evening).

New plan (Paul-approved, Hermes reviewing):

1. **Track 1 — Adversarial Suite** (internal, hand-curated, publishable): 100 turns across 6 categories × 3 domains (Option C: 60 banking + 20 healthcare + 20 legal), two-person rating with Cohen's Kappa. Direct measurement of DQL precision, recall, F1 per axis, axis orthogonality. Cost: ~$5-15. Time: 1-2 days.
2. **Track 2 — AgentDojo** (external, arxiv-cited): 100-300 USD budget with strict guardrails. External reproduction on attack-detection benchmark from ETH Zurich (Debenedetti et al., 2024).
3. **Track 3 — τ² (paused, may resume)**: adapter and A/B findings preserved in `experiments/tau2/`. Re-visit only after Track 1 + 2 are in.

## Decisions locked in (2026-07-09 20:47 CEST, Paul + Hermes)

- **Suite size:** 100 turns across 6 categories (17-17-17-17-16-16). Paul's Pure PASS control kept.
- **Domain split:** 60 Banking + 20 Healthcare + 20 Legal (Paul's Option C, Hermes' Banking-only vorschlag überstimmt).
- **Rating:** two-person (Perplexity curator + Raul reviewer), Cohen's Kappa reported. Dissens dokumentiert, nicht erzwungen. No LLM-as-judge.
- **Difficulty split per category:** 3 obvious / ~11 medium / 3 hard.
- **Read-marker convention:** proposed_action may include `[READ-ONLY retrieval]` prefix; runner evaluates DQL with and without marker to measure v0.2 defect mitigation delta.
- **Determinismus-Probe (2026-07-09 20:41 CEST):** 24 identische Calls, 24/24 Aggregates stabil BLOCK, 18/20 Achsen-Zellen stabil, 2 Flips bei Confidence ≤ 0.86. Aggregate-Determinismus 100%, Achsen-Micro-Jitter als dokumentiertes Kalibrierungs-Finding im Report. Curation freigegeben (Paul + Hermes).

## Structure now

```
dql-benchmark/
├── README.md
├── STATUS.md
├── suite/
│   ├── README.md
│   ├── schema.json               # JSON Schema for JSONL turns
│   ├── curation/                 # Category guidelines (done: all 6)
│   │   ├── 01_compliance_violation.md
│   │   ├── 02_prompt_injection.md
│   │   ├── 03_consent_missing.md
│   │   ├── 04_consistency_break.md
│   │   ├── 05_read_vs_write.md
│   │   └── 06_pure_pass.md
│   └── data/                     # JSONL turns (empty, awaiting Hermes go)
├── runner/                       # upcoming — DQL runner + F1 analysis
└── experiments/
    └── tau2/                     # paused, findings documented
```

## Done today (2026-07-09 evening)

- ✅ τ²-bench install + banking_knowledge smoke (task_001 baseline)
- ✅ τ² DQL adapter with read-only marker heuristic
- ✅ A/B live-DQL on task_001: 14/14 → 11/14 BLOCK, Consistency 11 → 4 (−64%)
- ✅ Two findings documented (read-vs-write confusion, consent-blindness)
- ✅ Strategic pivot to adversarial-suite + AgentDojo
- ✅ Repo restructured (τ² → `experiments/tau2/`, new `suite/` scaffolding)
- ✅ 6 category-guidelines written (curation-ready)
- ✅ JSON Schema for turn format
- ✅ Top-level README + STATUS

## Curation-Priorität

Start mit **consent_missing** + **read_vs_write** (Kategorien 3 + 5), da diese direkt die τ²-Findings testen. Danach Kategorien 1/2/4/6 in Reihenfolge.

## Estimated remaining cost — new plan

| Track | Cost | Kalenderzeit |
|---|---|---|
| Track 1 (Adversarial Suite, 100 turns × ~2 DQL calls) | $5-15 | 1-2 days |
| Track 2 (AgentDojo with guardrails) | $100-300 | 2-3 days |
| **Combined** | **$105-315** | **3-5 days** |

vs. abandoned τ² Full-Run estimate: **$3.500-4.000, 2-3 days, weaker metric.**

## Contact

Perplexity Computer (curator) — session continues from earlier sprint.
Hermes reviewing at ThoughtProof HQ.
Raul Jaeger (reviewer + final say).
