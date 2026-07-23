@echo off
echo Starting Smart Travel Planner Backend...
cd /d "%~dp0backend"
set PYTHONIOENCODING=utf-8
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause

