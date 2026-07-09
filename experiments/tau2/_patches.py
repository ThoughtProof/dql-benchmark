"""
SSL/HTTP patches required for running τ²-bench through the OpenServ endpoint
via the Perplexity agent-proxy (which uses a MITM CA missing AKI extensions
that Python's ssl module rejects).

Must be imported *before* litellm/openai/tau2 to take effect.

Trust model: this only disables TLS verification for the outbound HTTPS
connection from this sandbox. The connection still runs over an authenticated,
encrypted proxy tunnel — we're inside a trusted MITM by design.
"""
import os

# LiteLLM's own env-driven SSL toggle
os.environ.setdefault("LITELLM_SSL_VERIFY", "False")
os.environ.setdefault("SSL_VERIFY", "False")

import httpx  # noqa: E402

# Monkey-patch httpx client defaults so LiteLLM's internal OpenAI-SDK
# http_client (which is httpx-based) never enables verify.
_orig_client_init = httpx.Client.__init__
_orig_async_client_init = httpx.AsyncClient.__init__


def _patched_client_init(self, *args, **kwargs):
    kwargs.setdefault("verify", False)
    _orig_client_init(self, *args, **kwargs)


def _patched_async_client_init(self, *args, **kwargs):
    kwargs.setdefault("verify", False)
    _orig_async_client_init(self, *args, **kwargs)


httpx.Client.__init__ = _patched_client_init
httpx.AsyncClient.__init__ = _patched_async_client_init

# LiteLLM's module-level toggle
try:
    import litellm  # noqa: E402
    litellm.ssl_verify = False
except ImportError:
    pass
