' =====================================================
' Playlist Indexer - VBS Silent Launcher
' Runs Flask app WITHOUT showing console window
' =====================================================
'
' HOW IT WORKS:
' 1. WshShell.Run with parameter 0 = hidden window
' 2. "False" at end = don't wait for command to finish
' 3. WScript.Sleep pauses before opening browser
'
' TROUBLESHOOTING:
' - If app doesn't start, run start_app.bat to see errors
' - Check if port 5000 is already in use
' - Verify .venv exists and has all dependencies
'
' TO STOP THE APP:
' - Open Task Manager (Ctrl+Shift+Esc)
' - Find "python.exe" or "Python" process
' - End task
' =====================================================

Dim WshShell, projectPath

Set WshShell = CreateObject("WScript.Shell")

' Set your project path here
projectPath = "c:\Users\denko\Gemini\Antigravity\playlist_indexer"

' Change to project directory
WshShell.CurrentDirectory = projectPath

' Run Flask app silently (0 = hidden window, False = don't wait)
WshShell.Run "cmd /c .venv\Scripts\activate.bat && python web_app.py", 0, False

' Wait 2.5 seconds for server to start
WScript.Sleep 2500

' Open browser to the app
WshShell.Run "http://localhost:5000"

' Clean up
Set WshShell = Nothing
