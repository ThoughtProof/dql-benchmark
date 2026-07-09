"""
DQL adapter for τ²-bench traces.

Reads a τ² simulation trace, maps each assistant turn to a DQL verify call,
and emits per-step axis-fire annotations plus an aggregated per-simulation
DQL summary.

Design decisions:
- Only *assistant* turns are DQL-verified. Tool responses and user messages
  are context, never a "proposed action" to check.
- mandate = the most recent user message before this assistant turn
- proposed_action = the assistant tool_call name+args (if any), else the
  assistant content
- reasoning = the assistant content when a tool_call is fired (models
  often emit a rationale alongside the call). Falls back to a fixed string
  if the assistant emitted only a tool_call with no natural-language reasoning.
- context = task description + last N turns, capped at ~2000 chars, so DQL
  sees the salient prior state without being flooded.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

import httpx


DQL_URL = os.environ.get("DQL_URL", "https://dql.thoughtproof.ai")
DQL_VERIFY_ENDPOINT = f"{DQL_URL}/dql/verify"
DQL_TIMEOUT_S = 60.0
DQL_MAX_CONTEXT_CHARS = 2000
DQL_CONTEXT_TURN_WINDOW = 4  # last 4 messages before the assistant turn


AXES = ("intent", "scope", "risk", "consistency", "reversibility")


@dataclass
class DqlStepResult:
    """DQL verdict for one assistant turn in a τ² simulation."""
    turn_idx: int
    verdict: str  # ALLOW / BLOCK / REVIEW
    axes_fired: list[str] = field(default_factory=list)
    per_axis: dict[str, dict[str, Any]] = field(default_factory=dict)
    latency_ms: float = 0.0
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def _last_user_message(msgs: list[dict], before_idx: int) -> Optional[str]:
    for m in reversed(msgs[:before_idx]):
        if m.get("role") == "user":
            content = m.get("content")
            if content:
                return content
    return None


def _context_window(msgs: list[dict], before_idx: int, task_description: str = "") -> str:
    lines = []
    if task_description:
        lines.append(f"[TASK] {task_description}")
    start = max(0, before_idx - DQL_CONTEXT_TURN_WINDOW)
    for m in msgs[start:before_idx]:
        role = m.get("role", "?")
        content = m.get("content") or ""
        if not content:
            tcs = m.get("tool_calls") or []
            if tcs:
                names = [tc.get("name", "?") for tc in tcs]
                content = f"<tool_calls: {', '.join(names)}>"
        content = content[:400]
        lines.append(f"[{role}] {content}")
    text = "\n".join(lines)
    return text[:DQL_MAX_CONTEXT_CHARS]


# Prefix conventions from τ²-banking domain.
# Anything matching these is a read-only KB/DB call; must not be framed to
# DQL as a state-changing action or the risk axis over-fires.
READ_ONLY_TOOL_PREFIXES = (
    "KB_search", "kb_search", "search_", "list_", "get_", "find_",
    "lookup_", "retrieve_", "read_", "view_", "describe_", "check_",
    "grep", "BM25",
)


def _is_read_only_tool(name: str) -> bool:
    n = name or ""
    for p in READ_ONLY_TOOL_PREFIXES:
        if n.startswith(p):
            return True
    return False


def _extract_proposed_action(msg: dict) -> tuple[str, bool]:
    """Turn an assistant message into (proposed_action_string, is_read_only).

    is_read_only=True means: every tool call in this turn is a read-only
    retrieval / inspection. DQL should treat it as an information gathering
    step, not a state-changing action.
    """
    tcs = msg.get("tool_calls") or []
    if tcs:
        parts = []
        all_read = True
        for tc in tcs:
            name = tc.get("name", "?")
            args = tc.get("arguments", {})
            if isinstance(args, dict):
                args_str = json.dumps(args, separators=(",", ":"))[:400]
            else:
                args_str = str(args)[:400]
            if _is_read_only_tool(name):
                parts.append(f"[READ-ONLY retrieval] {name}({args_str})")
            else:
                all_read = False
                parts.append(f"[STATE-CHANGING action] {name}({args_str})")
        return " ; ".join(parts), all_read
    content = msg.get("content") or ""
    return content[:800] or "<empty assistant turn>", False


def _extract_reasoning(msg: dict) -> str:
    """Assistant content when a tool_call is fired often carries reasoning."""
    content = msg.get("content") or ""
    if content:
        return content[:600]
    # Model made a bare tool call with no prose — infer minimal reasoning
    tcs = msg.get("tool_calls") or []
    if tcs:
        first = tcs[0]
        return f"Model chose to invoke {first.get('name', 'a tool')} as the next step."
    return "Model emitted an empty turn."


def build_dql_request(
    msgs: list[dict],
    assistant_idx: int,
    task_description: str = "",
    sandbox: bool = False,
) -> dict:
    """Map one assistant turn in a τ² trace to a DQL /verify request body."""
    msg = msgs[assistant_idx]
    if msg.get("role") != "assistant":
        raise ValueError(f"msg at {assistant_idx} is not an assistant message")

    mandate = _last_user_message(msgs, assistant_idx) or task_description or "No prior user turn."
    proposed_action, is_read_only = _extract_proposed_action(msg)
    reasoning = _extract_reasoning(msg)
    context = _context_window(msgs, assistant_idx, task_description)

    # When the whole turn is read-only, annotate the context so DQL doesn't
    # over-index on the risk axis. State-changing tool calls remain plainly
    # framed as such (the framing is already in proposed_action).
    if is_read_only:
        context = (
            "[NOTE] This turn only invokes read-only retrieval tools. "
            "No external state changes; agent is gathering information.\n\n"
            + context
        )

    return {
        "mandate": mandate[:1500],
        "proposed_action": proposed_action[:1500],
        "reasoning": reasoning[:1500],
        "context": context[:DQL_MAX_CONTEXT_CHARS],
        "sandbox": sandbox,
    }


class DqlClient:
    """Sync DQL client — one HTTPX session, retries via httpx transport."""

    def __init__(
        self,
        url: str = DQL_VERIFY_ENDPOINT,
        timeout: float = DQL_TIMEOUT_S,
        verify_ssl: bool = False,  # sandbox uses agent-proxy MITM
    ):
        self.url = url
        self._client = httpx.Client(
            timeout=timeout,
            verify=verify_ssl,
            transport=httpx.HTTPTransport(retries=2),
        )

    def verify_step(
        self,
        msgs: list[dict],
        assistant_idx: int,
        task_description: str = "",
        sandbox: bool = False,
    ) -> DqlStepResult:
        body = build_dql_request(msgs, assistant_idx, task_description, sandbox)
        import time
        t0 = time.perf_counter()
        try:
            resp = self._client.post(self.url, json=body)
            latency_ms = (time.perf_counter() - t0) * 1000.0
            if resp.status_code != 200:
                return DqlStepResult(
                    turn_idx=assistant_idx,
                    verdict="ERROR",
                    latency_ms=latency_ms,
                    error=f"HTTP {resp.status_code}: {resp.text[:200]}",
                )
            data = resp.json()
        except Exception as e:
            latency_ms = (time.perf_counter() - t0) * 1000.0
            return DqlStepResult(
                turn_idx=assistant_idx,
                verdict="ERROR",
                latency_ms=latency_ms,
                error=f"{type(e).__name__}: {str(e)[:200]}",
            )

        agg = data.get("aggregate") or {}
        verdict = agg.get("verdict", "UNKNOWN")
        per_axis: dict[str, dict[str, Any]] = {}
        axes_fired: list[str] = []
        for axis_data in (data.get("axes") or []):
            axis_name = axis_data.get("axis")
            if not axis_name:
                continue
            per_axis[axis_name] = {
                "verdict": axis_data.get("verdict"),
                "confidence": axis_data.get("confidence"),
                "objection": (axis_data.get("objection") or "")[:300],
            }
            if axis_data.get("verdict") == "FAIL":
                axes_fired.append(axis_name)

        return DqlStepResult(
            turn_idx=assistant_idx,
            verdict=verdict,
            axes_fired=axes_fired,
            per_axis=per_axis,
            latency_ms=latency_ms,
        )

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def annotate_simulation(
    sim: dict,
    task_description: str = "",
    sandbox: bool = False,
    client: Optional[DqlClient] = None,
) -> dict:
    """Take one τ² simulation dict, run DQL on every assistant turn,
    return {step_results: [...], summary: {...}}.
    """
    own_client = client is None
    if own_client:
        client = DqlClient()

    msgs = sim.get("messages", [])
    step_results = []
    try:
        for i, m in enumerate(msgs):
            if m.get("role") != "assistant":
                continue
            # skip the trivial opener "Hi! How can I help you today?"
            content = m.get("content") or ""
            tcs = m.get("tool_calls") or []
            if not tcs and len(content) < 30:
                continue
            r = client.verify_step(msgs, i, task_description, sandbox)
            step_results.append(r.to_dict())
    finally:
        if own_client:
            client.close()

    n = len(step_results)
    n_block = sum(1 for r in step_results if r["verdict"] == "BLOCK")
    n_review = sum(1 for r in step_results if r["verdict"] == "REVIEW")
    n_error = sum(1 for r in step_results if r["verdict"] == "ERROR")
    axis_fire_counts = {ax: 0 for ax in AXES}
    for r in step_results:
        for ax in r.get("axes_fired", []):
            if ax in axis_fire_counts:
                axis_fire_counts[ax] += 1
    summary = {
        "task_id": sim.get("task_id"),
        "trial": sim.get("trial"),
        "n_assistant_turns_checked": n,
        "n_block": n_block,
        "n_review": n_review,
        "n_error": n_error,
        "any_axis_fired": sum(1 for r in step_results if r["axes_fired"]),
        "axis_fire_counts": axis_fire_counts,
        "task_reward": (sim.get("reward_info") or {}).get("reward"),
    }
    return {"step_results": step_results, "summary": summary}


if __name__ == "__main__":
    import sys
    results_path = sys.argv[1] if len(sys.argv) > 1 else \
        "/tmp/tau2-bench/data/simulations/20260709_170621_banking_knowledge_llm_agent_claude-sonnet-5_user_simulator_claude-sonnet-5/results.json"
    with open(results_path) as f:
        results = json.load(f)
    sim = results["simulations"][0]
    task_id = sim["task_id"]
    task_description = ""
    for t in results.get("tasks", []):
        if t.get("id") == task_id:
            desc = t.get("description")
            if isinstance(desc, dict):
                task_description = desc.get("purpose", "") or ""
            elif isinstance(desc, str):
                task_description = desc
            break

    print(f"Annotating {task_id} (trial {sim.get('trial')})...")
    out = annotate_simulation(sim, task_description=task_description, sandbox=True)
    print(json.dumps(out["summary"], indent=2))
    print()
    print("=== Per-step verdicts ===")
    for r in out["step_results"]:
        fired = ",".join(r["axes_fired"]) or "-"
        err = f" ERR={r['error'][:60]}" if r["error"] else ""
        print(f"  turn {r['turn_idx']:3d}  {r['verdict']:8s}  fired=[{fired}]  {r['latency_ms']:.0f}ms{err}")
