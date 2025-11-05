@echo off
call .venv\Scripts\activate
uvicorn web.main:app --reload
pause
