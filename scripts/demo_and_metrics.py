#!/usr/bin/env python3
"""
Hit the running router with a mix of light/heavy prompts, then print
the exact metrics you need for the portfolio write-up.

Usage (local):
  uvicorn main:app --reload &
  python scripts/demo_and_metrics.py

Usage (deployed):
  python scripts/demo_and_metrics.py --base-url https://your-app.up.railway.app
"""

import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx

# Mix of prompts that should exercise light, heavy, and cache paths
PROMPTS = [
    # Light (should route to Haiku)
    "What is the capital of France?",
    "Define recursion in one sentence.",
    "Translate 'good morning' to Spanish.",
    "What is 15 * 7?",
    "List three primary colors.",
    "Summarize in one line: The cat sat on the mat.",
    # Near-duplicates for cache hits
    "What's the capital of France?",
    "Tell me the capital city of France.",
    "Capital of France please.",
    # Heavy (should route to Sonnet)
    "Design a fault-tolerant architecture for a multi-region payments system, comparing eventual vs strong consistency trade-offs.",
    "Explain step by step why a Docker container might keep getting OOM-killed and propose a refactor of the memory allocation strategy.",
    "Compare the trade-offs of using Redis vs Postgres for a high-throughput session store and recommend an architecture.",
    "Debug this and propose a fix:\n```python\ndef average(nums):\n    return sum(nums) / len(nums)\n```\nIt crashes on empty lists.",
    "Architect a secure multi-tenant SaaS billing system with RBAC and audit logging.",
]


def call_chat(client: httpx.Client, base: str, prompt: str) -> dict:
    start = time.perf_counter()
    try:
        r = client.post(f"{base}/chat", json={"prompt": prompt}, timeout=60.0)
        latency_ms = (time.perf_counter() - start) * 1000
        data = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        data["_latency_ms"] = round(latency_ms, 1)
        data["_status"] = r.status_code
        data["_prompt_preview"] = prompt[:60]
        return data
    except Exception as e:
        return {
            "_error": str(e),
            "_latency_ms": (time.perf_counter() - start) * 1000,
            "_prompt_preview": prompt[:60],
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    print(f"Target: {base}")
    print("Checking /health ...")
    with httpx.Client() as client:
        health = client.get(f"{base}/health", timeout=10)
        print(f"  health → {health.status_code} {health.json()}")

        print(f"\nSending {len(PROMPTS)} prompts ({args.workers} workers) ...\n")
        results = []
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(call_chat, client, base, p) for p in PROMPTS]
            for fut in as_completed(futures):
                results.append(fut.result())

        stats = client.get(f"{base}/stats", timeout=10).json()

    ok = [r for r in results if r.get("_status") == 200 and "error" not in r]
    cache_hits = [r for r in ok if r.get("cache_hit")]
    light = [r for r in ok if r.get("route") == "light"]
    heavy = [r for r in ok if r.get("route") == "heavy"]
    latencies = sorted(r["_latency_ms"] for r in ok)

    def pct(n, d):
        return round(100 * n / d, 1) if d else 0.0

    def percentile(data, p):
        if not data:
            return None
        k = (len(data) - 1) * p / 100
        f = int(k)
        c = min(f + 1, len(data) - 1)
        return round(data[f] + (data[c] - data[f]) * (k - f), 1)

    print("=" * 60)
    print("PORTFOLIO METRICS (copy these into your README / write-up)")
    print("=" * 60)
    print(f"Total successful requests : {len(ok)} / {len(results)}")
    print(f"Cache hit rate            : {pct(len(cache_hits), len(ok))}%  ({len(cache_hits)} hits)")
    print(f"Routed to light (Haiku)   : {pct(len(light), len(ok))}%")
    print(f"Routed to heavy (Sonnet)  : {pct(len(heavy), len(ok))}%")
    print(f"p50 latency               : {percentile(latencies, 50)} ms")
    print(f"p95 latency               : {percentile(latencies, 95)} ms")
    print()
    print("Server-side /stats:")
    print(json.dumps(stats, indent=2))
    print()
    print("Sample responses:")
    for r in ok[:5]:
        route = r.get("route", "?")
        hit = "HIT" if r.get("cache_hit") else "miss"
        print(f"  [{route:5}] [{hit:4}] {r.get('_latency_ms')}ms  {r['_prompt_preview']!r}")
        if "response" in r:
            print(f"           → {str(r['response'])[:80]}...")
    print()
    print("Next: open your Langfuse dashboard, grab a good trace screenshot,")
    print("and paste the numbers above into the README under 'Key metrics'.")


if __name__ == "__main__":
    main()
