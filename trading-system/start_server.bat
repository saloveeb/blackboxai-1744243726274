@echo off
REM Windows batch file to start the trading system
set PYTHONPATH=.
uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
