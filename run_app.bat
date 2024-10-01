@echo off

REM Check current execution policy
powershell -Command "$policy = Get-ExecutionPolicy -Scope Process; if ($policy -ne 'Unrestricted') { Set-ExecutionPolicy Unrestricted -Scope Process; Write-Host 'Execution policy set to Unrestricted for this process.' } else { Write-Host 'Execution policy is already Unrestricted.' }"

REM Check if virtual environment exists, create if it doesn't
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Check if requirements are installed
python -c "import feedparser, requests, PIL, tkhtmlview" 2>nul
if %errorlevel% neq 0 (
    echo Installing requirements...
    pip install -r requirements.txt
) else (
    echo Requirements already installed.
)

REM Run the main Python script
python main.py

REM Deactivate the virtual environment
call venv\Scripts\deactivate.bat

REM Pause to keep the window open after the script finishes
pause
