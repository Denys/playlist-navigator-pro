@echo off
REM =====================================================
REM Playlist Indexer - Batch Launcher
REM Shows console window (useful for debugging)
REM =====================================================

cd /d "c:\Users\denko\Gemini\Antigravity\playlist_indexer"

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Open browser after short delay (in background)
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://localhost:5000"

REM Start the Flask app (this keeps the console open)
python web_app.py

REM If app exits, pause to see any error messages
pause
