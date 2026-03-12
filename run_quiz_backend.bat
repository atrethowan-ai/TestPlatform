@echo off
REM Activate venv if not already active
if exist .venv\Scripts\activate (
    call .venv\Scripts\activate
)
REM Set PYTHONPATH to kids_learning_system\quiz_pipeline\src
set PYTHONPATH=%CD%\kids_learning_system\quiz_pipeline\src
cd kids_learning_system\quiz_pipeline\src
uvicorn quiz_pipeline.local_service.app:app --host 127.0.0.1 --port 8000
