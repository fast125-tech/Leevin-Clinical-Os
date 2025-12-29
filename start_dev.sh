#!/bin/bash
echo "🚀 KAIROS Clinical OS - System Startup..."

# 1. Install Dependencies (Quietly)
echo "📦 Checking Dependencies..."
pip install -r requirements.txt -q

# 2. Run Tests
echo "🧪 Running Logic Tests..."
pytest tests/ -q --tb=short

if [ $? -eq 0 ]; then
    echo "✅ Tests Passed. Launching UI..."
    # 3. Launch App
    streamlit run app_ui.py --server.port 8080 --server.address 0.0.0.0
else
    echo "❌ Tests Failed. Aborting Launch."
    echo "Please fix the errors above."
    exit 1
fi
