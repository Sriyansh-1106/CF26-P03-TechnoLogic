# PowerShell launcher for VeriFlow
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Starting VeriFlow Master Safety Dashboard..." -ForegroundColor Green
Write-Host "  URL: http://localhost:8501" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
python -m streamlit run app.py
