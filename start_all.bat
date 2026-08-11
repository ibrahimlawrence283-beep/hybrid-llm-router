@echo off
title Meridian Telemetry Engine Launcher

:: Navigate to Project Directory
cd /d E:\hybrid-llm-router

:: Launch FastAPI Backend in a new terminal window
start "Meridian FastAPI Engine" cmd /k "python -m uvicorn main:app --port 8000 --reload"

:: Wait 3 seconds for API initialization
timeout /t 3 /nobreak > nul

:: Launch Streamlit Dashboard in a new terminal window
start "Meridian Telemetry Dashboard" cmd /k "python -m streamlit run dashboard.py"

exit
