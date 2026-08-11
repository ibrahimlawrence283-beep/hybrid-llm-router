# Meridian Telemetry & Governance Gateway

An enterprise-grade **Hybrid ML + LLM Router & Telemetry Gateway** designed to optimize AI infrastructure spend, enforce real-time cost governance in local currency (KES), reduce inference latency via semantic vector caching, and provide full request auditability.

## ??? Key Features
- **Semantic Vector Caching:** Bypasses LLM inference for duplicate/similar prompts (achieving ~12ms latency at zero cost).
- **Dynamic Tier Routing:** Routes standard queries to instant light models (`llama-3.1-8b`) and complex reasoning to heavy models (`gpt-4o`).
- **Financial Governance (KES):** Tracks real-time API spend and cost savings avoided in local currency.
- **Latency Benchmarking:** Real-time tracking of p50 (median) and p95 (tail) performance metrics.
- **Proof Ledger & Audit Trail:** Detailed log of similarity scores, target models, costs, and routing rationales.

## ?? Quickstart
Execute the single-click launcher to initialize the API gateway, run the benchmark suite, and launch the telemetry UI:
```cmd
run_app.bat
```

## ?? Tech Stack
- **Backend Gateway:** FastAPI, Uvicorn, Pydantic
- **Frontend Dashboard:** Streamlit, Plotly, Pandas
- **Scripting & Automation:** Windows Batch / Shell
