# experiments/tau2 — paused

**Status:** paused as of 2026-07-09.
**Reason:** cost explosion on complex tasks + wrong metric for DQL evaluation.

## What was here

An adapter that annotates [Sierra's τ²-bench](https://sierra.ai/blog/benchmarking-ai-agents) `banking_knowledge` simulations with DQL verdicts, plus a smoke-runner that routes Sonnet-5 through OpenServ (`inference-api.openserv.ai/v1`).

- `adapter.py` — `DqlClient` + `annotate_simulation()` that maps each assistant turn to `POST /dql/verify` and records verdict + per-axis fires. Includes a `[READ-ONLY retrieval]` marker heuristic that strips state-change signals from retrieval-only tool calls (kb_search etc.).
- `_patches.py` — httpx + LiteLLM `ssl_verify=False` workaround for the Perplexity Computer sandbox proxy (its MITM CA is missing the Authority Key Identifier extension, which Python `ssl` rejects).
- `run_smoke.py` — thin `tau2 run` wrapper that pins `--retrieval-config bm25_grep`, `temperature=0`, `seed=42`.

## Two findings before pause (worth citing in v0.3 roadmap)

Task_001, 14 assistant turns, live DQL calls to `dql.thoughtproof.ai` (v0.2 production).

| Metric | Without read-marker | With read-marker | Δ |
|---|---|---|---|
| BLOCK | 14/14 (100%) | 11/14 (79%) | −21pp |
| REVIEW | 0 | 3 | +3 |
| Risk-fires | 14 | 11 | −3 |
| Consistency-fires | 11 | 4 | **−7 (−64%)** |

**Finding 1 — Read-vs-Write confusion (mitigable):**
DQL v0.2 has no built-in distinction between retrieval and state-changing actions. A `kb_search` call receives the same treatment as a `transfer_funds` call. The read-only marker in `_extract_proposed_action()` reduces consistency fires by 64% on retrieval turns — a clean isolated effect. Roadmap: bake read-vs-write into the axis prompts in v0.3.

**Finding 2 — Consent-blindness (fundamental):**
Even when the user explicitly says "apply this now", DQL v0.2 sees only the potentially-risky action, not the user-consent in context. Turn 13 (`apply_for_credit_card` after explicit consent) fires all 5 axes — correct from DQL's view, but a false positive from the task's view. Roadmap: consent-awareness in the context construction, or explicit `user_consent: true` field in the DQL request schema.

## Why paused

**Cost:** task_002 ran 240s before manual kill and produced 300 Sonnet-5 requests on OpenServ (agent got stuck in a `kb_search` loop; 1.25 req/s until `--max-steps 200` hit). Extrapolated full-run (97 tasks × 4 trials × 3 tracks) was ~$3.500-4.000 rather than the initial $200-500 estimate. See OpenServ usage dashboard 2026-07-09 for actuals.

**Metric mismatch:** τ² measures task success, not DQL verdict quality. If DQL correctly blocks a risky action and the agent therefore fails the task, τ² counts it as failure. The metric doesn't map cleanly to the value proposition.

## How to resume (if we do)

Prerequisites before touching this again:
1. Strict guardrails: `--max-steps 20`, per-task cost cap, `--max-errors 2`.
2. Fixed metric: define a DQL-Verdict-Truth column separately from τ² reward, so we can measure DQL precision/recall independently of agent task success.
3. Smaller model for user simulator (Haiku 4.5 was ~99% cheaper than Sonnet-5 in the OpenServ Usage panel).

The adapter code is production-ready; only the runner and evaluation logic need the guardrails.
