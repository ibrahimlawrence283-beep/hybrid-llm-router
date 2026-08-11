# Meridian Telemetry & Governance Gateway

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

An enterprise-grade **Hybrid ML + LLM Router & Telemetry Gateway** designed to optimize AI infrastructure spend, enforce real-time cost governance in local currency (KES), reduce inference latency via semantic vector caching, and provide full request auditability.

---

## System Architecture

```text
+-------------------------------------------------------------+
|                      User / Application                     |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                FastAPI Telemetry Gateway                    |
|                        (main.py)                            |
+--------------+---------------+--------------+---------------+
               |               |              |
               v               v              v
  +------------------+  +--------------+  +------------------+
  | Vector Semantic  |  | Light Model  |  | Heavy Model      |
  | Cache (cache-v1) |  | (llama3.1-8b)|  | (gpt-4o)         |
  | Latency: ~12 ms  |  | Latency:~140ms|  | Latency: ~140 ms |
  | Cost: KSh 0.0000 |  | Cost:KSh0.104|  | Cost: KSh 0.455  |
  +------------------+  +--------------+  +------------------+
               |               |              |
               +---------------+--------------+
                               |
                               v
+-------------------------------------------------------------+
|                 Streamlit Control Dashboard                 |
|                        (dashboard.py)                       |
+-------------------------------------------------------------+

## Core Features

- **Semantic Vector Caching:** Bypasses LLM execution for duplicate or semantically identical queries, returning responses in ~12 ms at zero cost.
- **Dynamic Model Tier Routing:** Automatically routes routine queries to cost-effective light models (`llama-3.1-8b`) while directing complex reasoning prompts to heavy models (`gpt-4o`).
- **Financial Governance (KES):** Tracks real-time API expenditure and total cost savings avoided directly in Kenyan Shillings.
- **Latency Benchmarking:** Displays real-time median (p50) and tail (p95) latency distributions.
- **Proof Ledger & Audit Trail:** Provides transparent, row-by-row tracking of similarity scores, target models, query execution costs, and routing rationales.

---

## Quickstart

Execute the single-click launcher script in Command Prompt to initialize the FastAPI backend, execute the benchmarking suite, and launch the Streamlit control dashboard:

```cmd
run_app.bat
Tech Stack
Backend Gateway: FastAPI, Uvicorn, Pydantic

Frontend Dashboard: Streamlit, Plotly, Pandas

Automation & Orchestration: Windows Batch Scripting / Shell