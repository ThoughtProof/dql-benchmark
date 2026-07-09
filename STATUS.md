# Sprint Status — τ²-bench Track A

**Started:** 2026-07-09 evening
**Sprint budget:** 3 focused days
**Repo:** [ThoughtProof/dql-tau2-eval](https://github.com/ThoughtProof/dql-tau2-eval)

## Decisions locked in

- **Benchmark:** τ²-bench (Sierra, June 2025), `banking_knowledge` domain, **97 tasks** in full test split
- **Agent model:** `claude-sonnet-5` (Sonnet 4 is deprecated; confirmed via OpenServ smoke test)
- **User simulator:** `claude-sonnet-5` (τ² standard, same model both sides)
- **Provider route:** OpenServ (`inference-api.openserv.ai/v1`), OpenAI-compatible API. Same infrastructure as DQL v0.2 production. Sonnet-5 confirmed working (2026-07-09 18:58 CEST).
- **Retrieval config:** `bm25_grep` (BM25 + grep, no embeddings, no sandbox). Sierra-supported config, no external dependencies. Saves ~$5-15 in OpenAI embedding costs and avoids Docker-sandbox setup. Story stays clean: no third-party retrieval quality confounder in the DQL effect measurement.
- **Tracks:** A = Baseline, B1 = Observer, B2 = Retry (all three, single-model design)
- **Trials:** 4 per task (τ² Pass^k)
- **Determinism:** temperature 0, seed 42 (Sentinel-congruent)
- **Cost limit:** none — run to completion, real estimate ~$200-500 total

## What is done (Day 1 evening)

- ✅ Repo `dql-tau2-eval` created (public MIT, skeleton committed as `b293849`)
- ✅ Python 3.13 venv + τ²-bench installed
- ✅ `audioop-lts` shim for Python 3.13 compatibility (τ² still imports audioop unconditionally)
- ✅ `tau2 check-data` green — banking_knowledge domain visible, 97 tasks in test set
- ✅ OpenServ credential registered securely (`custom-cred:inference-api.openserv.ai`)
- ✅ Sonnet-5 smoke test via OpenServ passed (returns `anthropic/claude-sonnet-5-20260630`)

## What is next (Day 2 morning)

1. **LiteLLM config** — τ² uses LiteLLM internally. Point it at OpenServ as a custom OpenAI-compatible provider. Test with `tau2 run --domain banking_knowledge --agent-llm openai/claude-sonnet-5 --user-llm openai/claude-sonnet-5 --num-tasks 1 --num-trials 1 --retrieval-config bm25_grep --api-base https://inference-api.openserv.ai/v1`
2. **Smoke test (5 tasks, 1 trial, baseline only)** — cost ~$1-3. Confirms end-to-end pipeline before adapter work.
3. Then Day 2 afternoon: DQL adapter + Observer wrapper (Track B1).

## Open questions for Raul (morning kick-off)

_None — all setup decisions locked as of 2026-07-09 19:00 CEST._

## Estimated remaining cost

- Smoke: $1-3
- Pilot (10 tasks × 4 trials × 3 tracks): $15-40
- Full run (97 tasks × 4 trials × 3 tracks): $200-450
- **Total:** $215-490 (no embedding/sandbox costs — bm25_grep is self-contained)

