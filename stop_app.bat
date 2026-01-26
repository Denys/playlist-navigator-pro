@echo off
REM =====================================================
REM Playlist Indexer - Stop Running Instance
REM Kills any Python process running on port 5000
REM =====================================================

echo Stopping Playlist Indexer...

REM Find and kill process using port 5000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    echo Killing process with PID: %%a
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Done. Port 5000 should now be free.
pause
