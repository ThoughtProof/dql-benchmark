"""
Smoke-test runner: 1 task, 1 trial, banking_knowledge domain,
bm25_grep retrieval, no DQL — just proves the end-to-end
τ² pipeline works with Sonnet-5 via OpenServ.

Usage:
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt \\
    OPENAI_API_KEY=dummy \\
    python -m dql_tau2_eval.run_smoke
"""
# CRITICAL: patches must load before any tau2/litellm/openai import
from dql_tau2_eval import _patches  # noqa: F401

import sys
import os

# Sensible defaults if the caller forgot
os.environ.setdefault("OPENAI_API_KEY", "dummy-injected-by-proxy")

# τ² picks up TAU2_DATA_DIR
os.environ.setdefault("TAU2_DATA_DIR", "/tmp/tau2-bench/data")

# Build the τ² argv
argv = [
    "tau2", "run",
    "--domain", "banking_knowledge",
    "--task-set-name", "banking_knowledge",
    "--agent-llm", "openai/claude-sonnet-5",
    "--user-llm", "openai/claude-sonnet-5",
    "--agent-llm-args", '{"temperature": 0.0, "api_base": "https://inference-api.openserv.ai/v1", "seed": 42}',
    "--user-llm-args", '{"temperature": 0.0, "api_base": "https://inference-api.openserv.ai/v1", "seed": 42}',
    "--retrieval-config", "bm25_grep",
    "--num-tasks", "1",
    "--num-trials", "1",
    "--max-concurrency", "1",
    "--auto-resume",
]

sys.argv = argv

from tau2.cli import main  # noqa: E402
sys.exit(main())
