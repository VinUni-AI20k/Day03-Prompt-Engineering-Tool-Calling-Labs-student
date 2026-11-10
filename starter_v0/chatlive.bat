@echo off
REM Chay UI Streamlit cua agent. Go chatlive --server.port 8502 de doi cong.
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Chua co .venv. Chay truoc:
    echo   python -m venv .venv
    echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m streamlit run app.py %*
