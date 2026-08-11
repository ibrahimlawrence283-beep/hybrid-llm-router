"""
Tracing: every request logs a trace with routing decision, cache hit/miss,
model used, latency, and (approximate) cost — to both Langfuse (LLM-specific
observability, great dashboards out of the box) and OpenTelemetry (vendor-
neutral, shows you understand the broader distributed-tracing ecosystem).

Langfuse gives you the LLM-specific view (prompts, completions, cost/token
tracking) for your write-up screenshots. OTel spans are what you'd wire into
a real company's existing observability stack (Datadog/Grafana/etc).
"""

import os
import time
from contextlib import contextmanager

from langfuse import Langfuse
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# --- OpenTelemetry setup -----------------------------------------------
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("hybrid-llm-router")

# --- Langfuse setup ------------------------------------------------------
# Gracefully degrade if keys are missing (local smoke tests without Langfuse)
_langfuse_keys = (
    os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
)
langfuse = None
if _langfuse_keys:
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
    )

# Approximate list pricing per 1M tokens (input, output) in USD — Aug 2026.
# Sonnet 5 introductory $2/$10 is permanent through at least Aug 31 2026;
# after that the standard rate is $3/$15. Haiku 4.5 is $1/$5.
# Update these numbers before publishing real cost claims in your write-up.
MODEL_PRICING = {
    "claude-haiku-4-5-20251001": (1.00, 5.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "claude-sonnet-5": (2.00, 10.00),          # intro pricing through Aug 2026
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-opus-4-8": (5.00, 25.00),
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    in_price, out_price = MODEL_PRICING.get(model, (0.0, 0.0))
    return (input_tokens / 1_000_000) * in_price + (output_tokens / 1_000_000) * out_price


@contextmanager
def trace_request(prompt: str, route: str, cache_hit: bool):
    """
    Wraps a single router request with OTel span + Langfuse trace.
    Usage:
        with trace_request(prompt, route, cache_hit) as t:
            ... call model ...
            t.set_result(response_text, model_used, input_tokens, output_tokens)
    """
    start = time.time()
    span = tracer.start_span("router.request")
    lf_trace = None
    if langfuse is not None:
        lf_trace = langfuse.trace(
            name="router-request",
            input=prompt,
            metadata={"route": route, "cache_hit": cache_hit},
        )

    class _Handle:
        def set_result(self, response_text, model_used, input_tokens=0, output_tokens=0):
            latency_ms = (time.time() - start) * 1000
            cost = estimate_cost(model_used, input_tokens, output_tokens)
            span.set_attribute("route", route)
            span.set_attribute("cache_hit", cache_hit)
            span.set_attribute("model_used", model_used)
            span.set_attribute("latency_ms", latency_ms)
            span.set_attribute("cost_usd", cost)
            if lf_trace is not None:
                lf_trace.update(
                    output=response_text,
                    metadata={
                        "route": route,
                        "cache_hit": cache_hit,
                        "model_used": model_used,
                        "latency_ms": latency_ms,
                        "cost_usd": cost,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                    },
                )

    try:
        yield _Handle()
    finally:
        span.end()
