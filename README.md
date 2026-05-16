# SmartShip AI — GenAI Logistics Intelligence Platform

**🏆 Winner / Complete Submission for Antigravity-Level Hackathon**

An end-to-end AI + MLOps logistics platform that predicts shipment delays, explains risks using Generative AI (Google Gemini), and provides intelligent operational recommendations. Built for production-level scalability and precision.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red)](https://streamlit.io/)

**Repository:** [github.com/collegehk456-svg/supply_chain_delay_predictor](https://github.com/collegehk456-svg/supply_chain_delay_predictor)

---

## What it does

| Capability | Description |
|------------|-------------|
| **Delay Prediction** | Binary label + probability using XGBoost (22 engineered features) |
| **GenAI Explanations** | Translates SHAP values into natural language using Google Gemini Pro |
| **Smart Recommendations** | AI-suggested business playbooks (e.g., "Reroute shipment to Flight") |
| **Business Impact** | Calculates estimated loss and mitigation savings in USD |
| **MLOps Pipeline** | Drift monitoring (Evidently AI), MLflow, DVC, automated retrain API |
| **Dashboard** | Futuristic glassmorphism Streamlit command center |
| **API** | High-performance FastAPI with full Swagger docs |

### Model metrics (holdout)

| Metric | Value |
|--------|-------|
| ROC-AUC | **0.74** |
| Precision | **0.75** |
| Recall | **0.63** |
| F1 | **0.69** |
| Accuracy | **0.66** |

---

## Quick start (Windows)

```powershell
git clone https://github.com/collegehk456-svg/supply_chain_delay_predictor.git
cd supply_chain_delay_predictor

# Ensure you have Python installed and in your PATH.
# Set up Google Gemini API Key
$env:GENAI_API_KEY = "your_google_gemini_api_key"

# Install dependencies
pip install -r requirements.txt

# Dataset setup
if (-not (Test-Path data\raw\train.csv)) { New-Item -ItemType Directory -Force data\raw | Out-Null; Copy-Item Train.csv data\raw\train.csv }

# Train the XGBoost Model & ML Pipeline
$env:PYTHONPATH = (Get-Location)
python scripts\train.py --data-path data\raw\train.csv --output-path models\production\model.pkl

# Run API + dashboard
.\start.ps1
```

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:8501 |
| API docs | http://localhost:8000/docs |
| Health | http://localhost:8000/health |

**Flagship API:** `POST /api/v1/predict/logistics` — prediction + risk + priority + $ impact + playbooks.

---

## Project structure

```
supply_chain_delay_predictor/
├── backend/              # FastAPI server + GenAI integration
│   └── services/
│       ├── logistics_intelligence.py
│       ├── ai_chat_service.py
│       └── anomaly_service.py
├── frontend/             # Antigravity-level Streamlit UI
│   ├── main.py
│   └── views/            # Dashboard, Batch Processing, Analytics
├── src/ml_pipeline/      # Scikit-learn + XGBoost + SHAP pipeline
│   └── ai/
│       ├── explainer.py  # Google Gemini Integration
│       └── recommender.py
├── scripts/
│   ├── train.py          # Training orchestration (MLflow compatible)
│   └── monitor_drift.py  # Evidently AI drift detection
├── docs/                 # Hackathon materials (PPT, IEEE Paper, Scripts)
└── docker-compose.yml
```

---

## API highlights

```bash
# Full logistics intelligence
curl -X POST http://localhost:8000/api/v1/predict/logistics \
  -H "Content-Type: application/json" \
  -d '{"warehouse_block":"A","mode_of_shipment":"Ship","customer_care_calls":2,
       "customer_rating":3.5,"cost_of_the_product":5000,"prior_purchases":3,
       "product_importance":"Medium","gender":"M","discount_offered":25,"weight_in_gms":3000}'

# MLOps drift check
curl http://localhost:8000/api/v1/mlops/drift
```

---

## Docker

```bash
docker-compose up --build
```

---

## Hackathon Deliverables

See the **[docs/](docs/)** folder for the complete Hackathon suite:
- [HACKATHON_PPT.md](docs/HACKATHON_PPT.md) - Pitch deck content
- [DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) - Step-by-step presentation script
- [IEEE_PAPER.md](docs/IEEE_PAPER.md) - IEEE format documentation
- [RESUME_CONTENT.md](docs/RESUME_CONTENT.md) - ATS-ready bullet points

---

## Push to GitHub

```powershell
git add -A
git status   # verify no .env or .pkl files staged
git commit -m "feat: logistics intelligence API, MLOps drift/retrain, hackathon-ready platform"
git push origin main
```

Copy `.env.example` to `.env` for local secrets. **Do not commit** `.env`, `*.pkl`, or large CSV artifacts.

---

## License

MIT — see [LICENSE](LICENSE).
