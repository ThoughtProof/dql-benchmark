# DQL v0.3 Adversarial Suite — Baseline C Report

**Datum:** 2026-07-09
**Suite:** 100 curated turns (Option C: 60 banking + 20 healthcare + 20 legal)
**Verdict-Split:** 51 BLOCK / 13 REVIEW / 36 PASS
**Verglichene Systeme:** DQL v0.2 prod vs. 3 LLM-Judges (OpenServ)
**Judge-Prompt:** 5-Achsen-Rubric (intent, scope, risk, consistency, reversibility) mit gleichem Kontrakt wie DQL

---

## Headline

| System | Strict acc. | Relaxed acc. | Errors | Cat 6 FPR | Cat 5 read/write | p50 latency | p90 latency |
|---|---:|---:|---:|---:|---:|---:|---:|
| **DQL v0.2 prod** | 51/100 (51%) | 64/100 (64%) | 0 | **16/16 (100%)** | **0/16 (0%)** | 4122 ms | 5734 ms |
| **gpt-5.4-nano** | 93/100 (93%) | 97/100 (97%) | 0 | 0/16 (0%) | 13/16 (81%) | 2967 ms | 4467 ms |
| **gemini-2.5-flash-lite** | 94/100 (94%) | 97/100 (97%) | 3 | 0/16 (0%) | 16/16 (100%) | 1861 ms | 4636 ms |
| **claude-haiku-4.5** | 90/100 (90%) | 97/100 (97%) | 0 | 1/16 (6%) | 14/16 (88%) | 4162 ms | 5312 ms |

## Interpretation (kurz)

- **DQL v0.2 verliert deutlich gegen alle drei kommerziellen Sub-Frontier-Judges.** Der strict-Accuracy-Gap ist ~40 Punkte. Das ist keine Nuance — das ist eine Kalibrierungskrise.
- **Cat 6 (pure_pass) FPR = 100 % ist der Killer.** DQL blockt jeden benign turn. Die drei Judges liegen bei 0–6 % FPR.
- **Cat 5 (read_vs_write) 0 % bestätigt den v0.2-Bug** und zeigt: er ist *nicht* strukturell — Gemini schafft 16/16 mit derselben 5-Achsen-Rubric.
- **Relaxed = 97 %** bei allen drei Judges ⇒ Adversarial-Detection ist bei ihnen fast perfekt. DQLs Problem ist Kalibrierung/Präzision, nicht Recall.

---

## Per-Category strict accuracy

| Kategorie | DQL v0.2 | gpt-5.4-nano | gemini-2.5-flash-lite | claude-haiku-4.5 |
|---|---:|---:|---:|---:|
| compliance_violation | 15/17 | 16/17 | **17/17** | 16/17 |
| prompt_injection | 14/17 | **16/17** | 13/17 | **16/17** |
| consent_missing | 8/17 | **16/17** | **16/17** | 14/17 |
| consistency_break | 14/17 | 16/17 | **16/17** | 15/17 |
| read_vs_write | **0/16** | 13/16 | **16/16** | 14/16 |
| pure_pass | **0/16** | **16/16** | **16/16** | 15/16 |

## Per-Category relaxed accuracy

| Kategorie | DQL v0.2 | gpt-5.4-nano | gemini-2.5-flash-lite | claude-haiku-4.5 |
|---|---:|---:|---:|---:|
| compliance_violation | 17/17 | 17/17 | 17/17 | 17/17 |
| prompt_injection | 17/17 | 17/17 | 14/17 | 17/17 |
| consent_missing | 13/17 | 17/17 | 17/17 | 17/17 |
| consistency_break | 17/17 | 17/17 | 17/17 | 17/17 |
| read_vs_write | 0/16 | 13/16 | 16/16 | 14/16 |
| pure_pass | 0/16 | 16/16 | 16/16 | 15/16 |

## By difficulty (strict)

| Schwierigkeit | DQL v0.2 | gpt-5.4-nano | gemini-2.5-flash-lite | claude-haiku-4.5 |
|---|---:|---:|---:|---:|
| obvious (18) | 12/18 (67%) | 18/18 (100%) | 18/18 (100%) | 18/18 (100%) |
| medium (64) | 36/64 (56%) | 63/64 (98%) | 60/64 (94%) | 58/64 (91%) |
| hard (18) | 3/18 (17%) | 12/18 (67%) | 16/18 (89%) | 14/18 (78%) |

Bemerkenswert: DQL v0.2 hat auf **obvious** nur 67 % strict. Die Judges liegen bei 100 %. Der Rest ist REVIEW-Kollaps und Cat-6/Cat-5-Fehler.

---

## Cat 6 (pure_pass) — verdict distribution

Der wichtigste Kalibrierungswert. Jeder Fire ist Production-Friction.

| System | PASS | REVIEW | BLOCK | ERR |
|---|---:|---:|---:|---:|
| **DQL v0.2 prod** | 0 | 1 | **15** | 0 |
| gpt-5.4-nano | 16 | 0 | 0 | 0 |
| gemini-2.5-flash-lite | 16 | 0 | 0 | 0 |
| claude-haiku-4.5 | 15 | 1 | 0 | 0 |

DQL blockt "Good morning" (adv_085), veröffentlichte Filialöffnungszeiten (adv_086) und Standard-Legitimationsprüfungen. Die drei Judges lassen alle 16 durch.

## Cat 5 (read_vs_write) — verdict distribution

| System | PASS | REVIEW | BLOCK | ERR |
|---|---:|---:|---:|---:|
| **DQL v0.2 prod** | 0 | 0 | **16** | 0 |
| gpt-5.4-nano | 13 | 3 | 0 | 0 |
| gemini-2.5-flash-lite | 16 | 0 | 0 | 0 |
| claude-haiku-4.5 | 14 | 2 | 0 | 0 |

Der bekannte v0.2-Bug ist reproduzierbar. Kein Judge zeigt ihn.

---

## Axis fire distribution (Total-Fires über 100 turns)

| Achse | Erwartet | DQL v0.2 | gpt-5.4-nano | gemini-2.5-flash-lite | claude-haiku-4.5 |
|---|---:|---:|---:|---:|---:|
| intent | 48 | 49 (1.02×) | 43 (0.90×) | 54 (1.13×) | 57 (1.19×) |
| scope | 23 | 53 (2.30×) | 50 (2.17×) | 34 (1.48×) | 46 (2.00×) |
| **risk** | 38 | **99 (2.61×)** | 66 (1.74×) | 55 (1.45×) | 66 (1.74×) |
| consistency | 40 | 68 (1.70×) | 65 (1.63×) | 57 (1.43×) | 67 (1.68×) |
| reversibility | 39 | 53 (1.36×) | 56 (1.44×) | 52 (1.33×) | 59 (1.51×) |

Zwei Beobachtungen:

1. **DQLs risk-Achse feuert 99/100** — das ist der arithmetische Kern der 100 % Cat-6-FPR. Bei den Judges liegt risk zwischen 1.45× und 1.74× — hoch, aber nicht pathologisch.
2. **Alle Systeme über-feuern auf scope** (Faktor 1.5–2.3×). Das ist ein Ground-Truth-Signal, dass unsere Cat-6-Cases konservativer sind als das, was Sub-Frontier-LLMs als "PASS" akzeptieren würden. Aber DQL ist trotzdem der Ausreißer.

---

## Latenz-Distribution

| System | p50 | p90 |
|---|---:|---:|
| DQL v0.2 prod | 4122 ms | 5734 ms |
| gpt-5.4-nano | 2967 ms | 4467 ms |
| gemini-2.5-flash-lite | **1861 ms** | 4636 ms |
| claude-haiku-4.5 | 4162 ms | 5312 ms |

Gemini 2.5 Flash Lite ist ~2.2× schneller als DQL v0.2. Das ist eine zweite verlorene Achse — DQL v0.2 ist weder genauer noch schneller.

---

## Strategische Takeaways

### 1. Die Suite ist valide
Der Punkt der Adversarial Suite war: reproduzierbar messen. Sie tut das. Alle vier Systeme wurden gegen dieselben 100 curierten turns mit derselben 5-Achsen-Rubric evaluiert. Die Streuung (0–94 % strict) beweist, dass das Benchmark diskriminierend ist.

### 2. DQL v0.2 ist nicht die Baseline — es ist das Anti-Muster
Ein GPT-5.4-nano-Call mit unserer eigenen 5-Achsen-Rubric schlägt DQL v0.2 um 42 Punkte strict. Das heißt: unser aktueller Judge (v0.2) ist strikt schlechter als "nimm einen billigen LLM und gib ihm unsere Rubric".

### 3. Der v0.3-Fix ist konkret
Aus den Zahlen fallen drei kalibrierbare Ziele:

- **risk-Achse muss von 2.61× auf ~1.5× runter.** Wahrscheinlich Rubric-Rewrite und/oder Threshold-Anpassung.
- **read/write-Detection ist strukturell möglich** (Gemini: 16/16). Der v0.2-Bug ist ein Prompt- oder Threshold-Fehler, nicht ein LLM-Limit.
- **REVIEW-Kollaps zu BLOCK** muss verhindert werden. Die 13 REVIEW-Ground-Truths gehen bei DQL v0.2 komplett verloren.

### 4. Was v0.3 mindestens erreichen muss

Um öffentlich sagbar zu sein, muss DQL v0.3:

- ≥ 90 % strict accuracy
- ≤ 5 % Cat-6 FPR
- ≥ 80 % Cat-5 accuracy
- p50 ≤ 3 s

Sonst ist die Value-Prop gegenüber "einfach GPT-5.4-nano mit unserer Rubric aufrufen" nicht defendable.

### 5. Warum das trotzdem eine gute Story ist
Die Suite war explizit gebaut, um v0.2 zu brechen. Sie hat gebrochen, was sie brechen sollte. Das ist wissenschaftlich sauber und externalisierbar. Blog-Ton: "Wir haben unser eigenes System evaluiert, das Ergebnis war unbequem, wir haben v0.3 daraus abgeleitet."

---

## Reproducibility

- Suite: `suite/data/*.jsonl` (100 turns, 6 Kategorien, 2-Rater-Kappa in `REVIEWS.jsonl`)
- Runner: `runner/run_baseline_llm.py --workers 3` (mit 429-Backoff)
- Ergebnisse: `runs/results_baseline_*.jsonl` (300 rows total)
- OpenServ endpoint: `https://inference-api.openserv.ai/v1/chat/completions`
- Judge-Prompt: identisch zu DQL v0.2 5-Achsen-Rubric (siehe `runner/run_baseline_llm.py` JUDGE_PROMPT)

## Bekannte Limitationen

- **Kein OpenAI Moderation / Llama Guard** auf OpenServ — Track B (spezialisierte Moderationsmodelle) muss separat aufgesetzt werden, sobald Zugang klar ist.
- **Judge-Selbstevaluation ist nicht adversarial-getestet.** Ein OpenServ-Judge könnte gegen andere DQL-Prompts anders performen.
- **Cat 5 hat 16 turns, nicht 17** — Konsistent mit Suite-Aufbau (Cat 5 + 6 sind 16, andere 17).
- **claude-haiku-4.5 lief mit 2 Workern statt 3** (Rate-Limit-Recovery). Latenz-Zahlen sind vergleichbar (kein Batching-Effekt).
