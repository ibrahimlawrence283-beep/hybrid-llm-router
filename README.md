<div align="center">

# Meridian Telemetry & Governance Gateway

**An enterprise-grade Hybrid ML + LLM Router that cuts AI inference cost and latency through dynamic model-tier routing, semantic caching, and real-time financial governance.**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)

</div>

---

## Overview

Meridian sits between user query traffic and downstream LLMs (Llama 3.1 8B, GPT-4o), acting as a smart traffic controller and cost-governance layer. Instead of sending every request to an expensive, high-tier model, it:

- **Caches semantically** — near-duplicate queries are served from a vector cache instead of hitting an LLM at all
- **Routes dynamically** — simple prompts go to a fast, cheap model; complex ones escalate to a top-tier model
- **Tracks spend in real time** — every request is logged with cost, latency, and routing rationale, denominated in KES

## System Architecture

```
                     ┌───────────────────────────────────────┐
                     │            User / Application          │
                     └────────────────────┬────────────────────┘
                                           │
                                           ▼
                     ┌───────────────────────────────────────┐
                     │        FastAPI Telemetry Gateway        │
                     │               (main.py)                 │
                     └──────┬──────────────────┬───────────────┘
                            │                  │
           ┌────────────────┴────────┐        └──────────────────────────┐
           ▼                         ▼                                   ▼
┌──────────────────────┐  ┌──────────────────────┐          ┌──────────────────────┐
│  Vector Semantic      │  │  Light Model Tier     │          │  Heavy Model Tier     │
│  Cache (cache-v1)     │  │  (llama-3.1-8b)       │          │  (gpt-4o)             │
│  Latency: ~12 ms      │  │  Latency: ~140 ms     │          │  Latency: ~140 ms     │
│  Cost: KSh 0.0000     │  │  Cost: ~KSh 0.104     │          │  Cost: ~KSh 0.455     │
└──────────────────────┘  └──────────────────────┘          └──────────────────────┘
                                     │
                                     ▼
                     ┌───────────────────────────────────────┐
                     │       Streamlit Control Dashboard       │
                     │             (dashboard.py)               │
                     └───────────────────────────────────────┘
```

## Core Components

### 1. API Telemetry Gateway — `main.py`
Built on **FastAPI**.

- **Semantic Caching Engine** — checks incoming prompts against a vector index; a similarity score above `0.94` serves a cached hit in ~12 ms at KSh 0.00
- **Dynamic Model Tier Routing** — driven by a trained ML classifier, not a length threshold (see [Complexity Classifier](#complexity-classifier) below)
  | Tier | Model | Cost/request |
  |------|-------|---------------|
  | Light | `llama-3.1-8b` | ~KSh 0.104 |
  | Heavy | `gpt-4o` | ~KSh 0.455 |
- **Metrics Tracker** — logs total requests, cache hit ratio, latency distribution (p50/p95), actual API spend, and cost savings avoided (KES)

### Complexity Classifier

Routing is decided by a **TF-IDF + logistic regression classifier** trained on hand-labeled prompt examples, not a character-count heuristic. This is the "ML" in "Hybrid ML + LLM Router."

- **94% accuracy** on held-out examples
- Correctly routes cases where length alone is misleading — e.g. `"Why does this recursive function overflow?"` (44 characters, correctly routed **heavy**) and a padded, polite-but-trivial 120-character request (correctly routed **light**)
- Fully interpretable: inspecting the model's learned weights against the vocabulary surfaces the terms driving each decision — `trade-offs`, `architecture`, `design`, `explain` push toward **heavy**; `what`, `translate`, `define`, `give me` push toward **light**
- Trains in under a second on CPU with `train_classifier.py`, no model download required
- Designed to improve over time: as real traffic flows through the Proof Ledger, mis-routed prompts get hand-corrected and added to `training_data.py`, then the classifier is retrained on the growing, real-traffic-informed dataset

### 2. Automated Benchmarking Engine — `benchmark.py`
- Simulates real-world workload: standard queries, duplicate/semantic-repeat queries, and complex multi-paragraph prompts
- Pre-populates the gateway's in-memory telemetry state on startup so the dashboard has live data immediately

### 3. Real-Time Telemetry Dashboard — `dashboard.py`
- Dark-themed UI with Meridian Data Assurance branding and a responsive sidebar
- **Financial & performance KPIs**: total requests, hit rate, API spend, avoided cost, p50/p95 latency
- **Interactive visualizations**: Plotly doughnut chart (cache hit vs. miss) and bar chart (model tier breakdown)
- **Proof Ledger** — an audit log of every request: target model, similarity score, latency, cost, and routing rationale
- **Live Sandbox** — manually test custom prompts and watch the routing decision happen in real time

### 4. One-Click Startup Orchestrator — `run_app.bat`
- Terminates stale Python processes
- Spawns the FastAPI backend silently on port `8000`
- Runs `benchmark.py` to seed telemetry
- Launches the Streamlit UI on port `8501`

## Tech Stack

| Layer | Technology |
|---|---|
| Backend Gateway | FastAPI, Uvicorn, Pydantic |
| Frontend Dashboard | Streamlit, Plotly, Pandas |
| Caching | Vector similarity search (semantic_cache.py) |
| Orchestration | Windows Batch scripting |
| Models | Llama 3.1 8B (light tier), GPT-4o (heavy tier) |

## Quickstart

```cmd
run_app.bat
```

This single command starts the FastAPI backend, seeds telemetry via the benchmark engine, and launches the dashboard. Once running:

- API: [http://localhost:8000](http://localhost:8000)
- Dashboard: [http://localhost:8501](http://localhost:8501)

> **Note:** after `benchmark.py` finishes seeding telemetry, the dashboard needs a manual refresh (F5) to pick up the new numbers — Streamlit's `st.cache_data(ttl=1)` still requires a script rerun, it doesn't auto-poll a live tab.

## Project Structure

```
hybrid-llm-router/
├── main.py                # FastAPI telemetry gateway
├── dashboard.py            # Streamlit control dashboard
├── benchmark.py             # Workload simulation / telemetry seeding
├── semantic_cache.py        # Vector similarity cache engine
├── complexity_classifier.py # Trained ML router (TF-IDF + logistic regression)
├── train_classifier.py      # Retrains the classifier on training_data.py
├── training_data.py         # Hand-labeled prompt examples for training
├── routing/                # Model tier routing logic
├── cache/                  # Cache storage/index
├── observability/           # Tracing & metrics
├── scripts/                 # Load testing / utility scripts
├── tests/                   # Test suite
├── run_app.bat               # One-click startup orchestrator
├── start_all.bat             # Alternate startup script
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Key Metrics Tracked

- **Cache hit rate** — % of requests served from the semantic cache
- **Tier distribution** — % of live requests routed to light vs. heavy models
- **Latency** — p50 and p95, end to end
- **Cost governance** — actual API spend vs. cost avoided, tracked in KES

### Results from a live benchmark run (90 requests)

| Metric | Value |
|---|---|
| Total requests | 90 |
| Cache hit rate | **80.0%** (72 hits) |
| Routing split | ~74% light (`llama-3.1-8b`) / ~26% heavy (`gpt-4o`) |
| p50 latency | 0.01 ms |
| p95 latency | 4.06 ms |
| Actual API spend | KSh 0.1413 |
| Cost avoided via caching | KSh 2.1000 |
| **Effective cost reduction** | **~93.7%** vs. an all-heavy-model baseline |

<img width="1240" height="588" alt="Screenshot_12-8-2026_91831_localhost" src="https://github.com/user-attachments/assets/1462ea6b-b555-48b8-bdee-9d9d216b7638" />
<img width="1240" height="588" alt="Screenshot_12-8-2026_9185_localhost" src="https://github.com/user-attachments/assets/40370655-93d4-4029-94c8-2f8565dc5e50" />
<img width="1240" height="588" alt="Screenshot_12-8-2026_91744_localhost" src="https://github.com/user-attachments/assets/b20aecf5-af78-4062-8043-8f8ee9c9cd4e" />


## Roadmap

- [x] Swap the length-based router for a trained complexity classifier
- [ ] Retrain the classifier on real production traffic pulled from the Proof Ledger
- [ ] Upgrade the classifier's features from TF-IDF to sentence embeddings for better generalization, once traffic volume justifies the added dependency
- [ ] Persist the semantic cache (Redis/pgvector) instead of in-memory
- [ ] Add authenticated multi-tenant cost tracking
- [ ] Deploy behind a public URL for live demo access

## License

copyright Meridian Data Assurance
