@echo off
setlocal
cd /d %~dp0
start "" http://127.0.0.1:5000
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 -c "import flask, requests" >nul 2>nul
  if errorlevel 1 (
    echo Installing required packages...
    py -3 -m pip install -r requirements.txt
  )
  echo Starting Pick Dashboard...
  py -3 app.py
  pause
  exit /b
)
where python >nul 2>nul
if %errorlevel%==0 (
  python -c "import flask, requests" >nul 2>nul
  if errorlevel 1 (
    echo Installing required packages...
    python -m pip install -r requirements.txt
  )
  echo Starting Pick Dashboard...
  python app.py
  pause
  exit /b
)
echo Python 3 was not found. Please install Python 3 first.
pause
