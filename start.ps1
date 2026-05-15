# SmartShip AI — Windows quick start (fixed)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$env:PYTHONPATH = $PSScriptRoot
$env:API_URL = "http://localhost:8000"

# Stop stale processes on our ports
foreach ($port in @(8000, 8501)) {
    Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}
Start-Sleep -Seconds 1

if (-not (Test-Path "data\raw\train.csv") -and (Test-Path "Train.csv")) {
    New-Item -ItemType Directory -Force -Path "data\raw" | Out-Null
    Copy-Item "Train.csv" "data\raw\train.csv"
}

if (-not (Test-Path "models\production\full_pipeline.pkl")) {
    Write-Host "Training model (first run)..."
    python scripts\train.py --data-path data\raw\train.csv --output-path models\production\model.pkl
}

New-Item -ItemType Directory -Force -Path "logs" | Out-Null

Write-Host "Starting API on http://localhost:8000 ..."
$apiLog = Join-Path $PSScriptRoot "logs\api.log"
$apiErr = Join-Path $PSScriptRoot "logs\api.err.log"
$apiProc = Start-Process python -ArgumentList @(
    "-m", "uvicorn", "backend.main:app",
    "--host", "127.0.0.1", "--port", "8000"
) -WorkingDirectory $PSScriptRoot -RedirectStandardOutput $apiLog -RedirectStandardError $apiErr -PassThru

# Wait for API health (up to 90s — model load can be slow)
$healthy = $false
for ($i = 0; $i -lt 45; $i++) {
    Start-Sleep -Seconds 2
    try {
        $r = Invoke-RestMethod "http://127.0.0.1:8000/health" -TimeoutSec 5
        if ($r.model_loaded) {
            $healthy = $true
            Write-Host "API ready (model loaded)."
            break
        }
    } catch { }
    Write-Host "  Waiting for API... ($($i + 1)/45)"
}

if (-not $healthy) {
    Write-Host "API failed to start. Last log lines:"
    if (Test-Path $apiErr) { Get-Content $apiErr -Tail 25 }
    if (Test-Path $apiLog) { Get-Content $apiLog -Tail 15 }
    Stop-Process -Id $apiProc.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

function Stop-ApiProcess {
    param([System.Diagnostics.Process]$Proc)
    if (-not $Proc -or $Proc.HasExited) { return }
    try {
        $Proc.CloseMainWindow() | Out-Null
        if (-not $Proc.WaitForExit(3000)) {
            Stop-Process -Id $Proc.Id -Force -ErrorAction SilentlyContinue
        }
    } catch {
        Stop-Process -Id $Proc.Id -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Starting Dashboard on http://localhost:8501 ..."
Write-Host "Press Ctrl+C to stop both services."
Start-Process "http://localhost:8501"

$exitCode = 0
try {
    & python -m streamlit run frontend\main.py --server.port 8501 --server.address 127.0.0.1
    if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) { $exitCode = $LASTEXITCODE }
} catch {
    if ($_.Exception.Message -notmatch 'pipeline has been stopped|operation was canceled') {
        Write-Host "Dashboard error: $($_.Exception.Message)"
        $exitCode = 1
    }
} finally {
    Stop-ApiProcess -Proc $apiProc
    Write-Host "Stopped."
}
# Avoid unsigned -1 (4294967295) when child was force-stopped on Ctrl+C
if ($exitCode -lt 0) { $exitCode = 0 }
exit $exitCode
