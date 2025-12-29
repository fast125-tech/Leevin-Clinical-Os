Write-Host "KAIROS Clinical OS - System Startup..."

# 1. Install Dependencies
Write-Host "Checking Dependencies..."
pip install -r requirements.txt -q

# 2. Run Tests
Write-Host "Running Logic Tests..."
pytest tests/ -q --tb=short

if ($LASTEXITCODE -eq 0) {
    Write-Host "Tests Passed. Launching UI..."
    # 3. Launch App
    streamlit run app_ui.py --server.port 8080 --server.address 0.0.0.0
} else {
    Write-Host "Tests Failed. Aborting Launch."
    Write-Host "Please fix the errors above."
    exit 1
}
