# Meridian Telemetry & Governance Gateway

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

An enterprise-grade **Hybrid ML + LLM Router & Telemetry Gateway** designed to optimize AI infrastructure spend, enforce real-time cost governance in local currency (KES), reduce inference latency via semantic vector caching, and provide full request auditability.

---

## System Architecture
┌─────────────────────────────────────────┐
                     │          User / Application             │
                     └────────────────────┬────────────────────┘
                                          │
                                          ▼
                     ┌─────────────────────────────────────────┐
                     │       FastAPI Telemetry Gateway        │
                     │               (main.py)                 │
                     └──────┬──────────────────┬───────────────┘
                            │                  │
           ┌────────────────┴────────┐        └────────────────────────┐
           ▼                         ▼                                 ▼
┌──────────────────────┐  ┌──────────────────────┐          ┌──────────────────────┐
│  Vector Semantic     │  │  Light Model Tier    │          │  Heavy Model Tier    │
│  Cache (cache-v1)    │  │  (llama-3.1-8b)      │          │  (gpt-4o)            │
│  Latency: ~12 ms     │  │  Latency: ~140 ms    │          │  Latency: ~140 ms    │
│  Cost: KSh 0.0000    │  │  Cost: ~KSh 0.104    │          │  Cost: ~KSh 0.455    │
└──────────────────────┘  └──────────────────────┘          └──────────────────────┘
                                     │
                                     ▼
                     ┌─────────────────────────────────────────┐
                     │       Streamlit Control Dashboard       │
                     │             (dashboard.py)              │

                     └─────────────────────────────────────────┘
## Key Features
* **Semantic Vector Caching:** Bypasses LLM inference for duplicate/similar prompts (achieving ~12ms latency at zero cost).
* **Dynamic Tier Routing:** Routes standard queries to instant light models (`llama-3.1-8b`) and complex reasoning to heavy models (`gpt-4o`).
* **Financial Governance (KES):** Tracks real-time API spend and cost savings avoided in local currency.
* **Latency Benchmarking:** Real-time tracking of p50 (median) and p95 (tail) performance metrics.
* **Proof Ledger & Audit Trail:** Detailed log of similarity scores, target models, costs, and routing rationales.

## Quickstart
Execute the single-click launcher to initialize the API gateway, run the benchmark suite, and launch the telemetry UI:

```cmd
run_app.bat

## Tech Stack
* **Backend Gateway: FastAPI, Uvicorn, Pydantic

* **Frontend Dashboard: Streamlit, Plotly, Pandas

* **Automation & Orchestration: Windows Batch Scripting / Shell