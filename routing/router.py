import os
import hashlib
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

LIGHT_MODEL = os.getenv("LIGHT_MODEL", "llama-3.1-8b-instant").replace("groq/", "")
HEAVY_MODEL = os.getenv("HEAVY_MODEL", "llama-3.3-70b-versatile").replace("groq/", "")

PRICING = {
    LIGHT_MODEL: {"input": 0.05 / 1_000_000, "output": 0.08 / 1_000_000},
    HEAVY_MODEL: {"input": 0.59 / 1_000_000, "output": 0.79 / 1_000_000},
}

# In-Memory Cache Storage
RESPONSE_CACHE = {}

stats_counter = {
    "total_requests": 0,
    "cache_hits": 0,
    "light_model_requests": 0,
    "heavy_model_requests": 0,
    "total_tokens_processed": 0,
    "total_cost_usd": 0.0,
    "estimated_cost_saved_usd": 0.0,
}

def normalize_prompt(prompt: str) -> str:
    """Normalize whitespace and case for caching lookup."""
    return " ".join(prompt.strip().lower().split())

def hash_prompt(prompt: str) -> str:
    """Generate SHA256 hash for cache key generation."""
    return hashlib.sha256(normalize_prompt(prompt).encode('utf-8')).hexdigest()

def handle_request(prompt: str):
    stats_counter["total_requests"] += 1
    cache_key = hash_prompt(prompt)

    # 1. CHECK CACHE (Cache Hit)
    if cache_key in RESPONSE_CACHE:
        stats_counter["cache_hits"] += 1
        cached_entry = RESPONSE_CACHE[cache_key]
        
        # Estimate savings on cache hit (avoided heavy model call)
        estimated_heavy_cost = (cached_entry["usage"]["prompt_tokens"] * PRICING[HEAVY_MODEL]["input"]) + \
                               (cached_entry["usage"]["completion_tokens"] * PRICING[HEAVY_MODEL]["output"])
        stats_counter["estimated_cost_saved_usd"] += estimated_heavy_cost

        return {
            "model_used": cached_entry["model_used"],
            "response": cached_entry["response"],
            "cached": True,
            "usage": cached_entry["usage"],
            "metrics": {
                "estimated_cost_usd": 0.0,
                "cost_saved_vs_heavy_usd": round(estimated_heavy_cost, 6)
            }
        }

    # 2. CACHE MISS -> ROUTE TO MODEL
    if len(prompt.split()) > 30 or "architecture" in prompt.lower() or "design" in prompt.lower():
        selected_model = HEAVY_MODEL
        stats_counter["heavy_model_requests"] += 1
    else:
        selected_model = LIGHT_MODEL
        stats_counter["light_model_requests"] += 1

    response = client.chat.completions.create(
        model=selected_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1024,
    )

    usage = response.usage
    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens

    model_rates = PRICING.get(selected_model, {"input": 0.0, "output": 0.0})
    actual_cost = (prompt_tokens * model_rates["input"]) + (completion_tokens * model_rates["output"])

    heavy_rates = PRICING[HEAVY_MODEL]
    hypothetical_heavy_cost = (prompt_tokens * heavy_rates["input"]) + (completion_tokens * heavy_rates["output"])
    savings = max(0.0, hypothetical_heavy_cost - actual_cost)

    stats_counter["total_tokens_processed"] += total_tokens
    stats_counter["total_cost_usd"] += actual_cost
    stats_counter["estimated_cost_saved_usd"] += savings

    response_text = response.choices[0].message.content

    # Save to Cache
    RESPONSE_CACHE[cache_key] = {
        "model_used": selected_model,
        "response": response_text,
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
    }

    return {
        "model_used": selected_model,
        "response": response_text,
        "cached": False,
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        },
        "metrics": {
            "estimated_cost_usd": round(actual_cost, 6),
            "cost_saved_vs_heavy_usd": round(savings, 6),
        }
    }

def get_stats():
    return {
        **stats_counter,
        "total_cost_usd": round(stats_counter["total_cost_usd"], 6),
        "estimated_cost_saved_usd": round(stats_counter["estimated_cost_saved_usd"], 6),
    }