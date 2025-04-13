# PowerShell script to start both servers
Write-Host "Starting AI Trading Bot servers..." -ForegroundColor Green

# Start Flask backend in a new window
Write-Host "Starting Flask backend server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\api'; python app.py"

# Start React frontend in a new window
Write-Host "Starting React frontend server..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm start"

Write-Host "`nServers are starting in separate windows." -ForegroundColor Green
Write-Host "- Flask backend: http://localhost:5000" -ForegroundColor Yellow
Write-Host "- React frontend: http://localhost:3000" -ForegroundColor Yellow

Write-Host "`nPress Ctrl+C to exit this script, but the servers will continue running in their own windows." -ForegroundColor Magenta
Write-Host "To stop the servers, close their respective PowerShell windows." -ForegroundColor Magenta

# Keep the script running
while($true) {
    Start-Sleep -Seconds 60
} 