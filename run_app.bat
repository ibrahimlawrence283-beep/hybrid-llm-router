@echo off
title Meridian Telemetry Gateway
cd /d E:\hybrid-llm-router

:: Step 1: Terminate any existing Python background processes
taskkill /F /IM python.exe >nul 2>&1

:: Step 2: Start FastAPI backend silently in background
start /B python -m uvicorn main:app --port 8000

:: Step 3: Wait 3 seconds for backend initialization
timeout /t 3 /nobreak >nul

:: Step 4: Run benchmark script to populate telemetry data
python benchmark.py

:: Step 5: Launch Streamlit Dashboard
python -m streamlit run dashboard.py
