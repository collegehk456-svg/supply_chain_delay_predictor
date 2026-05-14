#!/bin/bash

echo "🚀 SmartShip AI - Quick Setup Script"
echo "========================================"

set -e

mkdir -p data/raw data/processed data/features models/production logs

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
pip install google-generativeai > /dev/null 2>&1

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env created. Please update with your API keys."
fi

echo "✅ Setup Complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Update .env with credentials"
echo "2. Train model: python scripts/download_and_train.py --download"
echo "3. Start API: uvicorn backend.main:app --reload --port 8000"
echo "4. Start Dashboard: streamlit run frontend/main.py"
