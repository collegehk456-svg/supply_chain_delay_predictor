# SmartShip AI — Supply Chain Delay Intelligence Platform

Production-style MLOps platform for **shipment delay prediction**, **explainable risk scoring**, **operational playbooks**, and **automated retraining** — built for the IEEE MLOps hackathon and real logistics workflows.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red)](https://streamlit.io/)

**Repository:** [github.com/collegehk456-svg/supply_chain_delay_predictor](https://github.com/collegehk456-svg/supply_chain_delay_predictor)

---

## What it does

| Capability | Description |
|------------|-------------|
| Delay prediction | Binary label + delay probability (XGBoost, 22 engineered features) |
| Risk tiers | LOW / MEDIUM / HIGH operational bands |
| Explainability | SHAP-style factors + natural language explanation |
| Business impact | Estimated loss, savings, net benefit (USD) |
| Prioritization | 0–100 priority score for fulfillment queues |
| MLOps | Drift monitoring, prediction logging, retrain API, MLflow in training |
| Dashboard | Streamlit command center for logistics managers |
| API | FastAPI with OpenAPI docs |

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

# Install dependencies
pip install -r requirements.txt

# Dataset: copy bundled Train.csv or place your CSV at data/raw/train.csv
if (-not (Test-Path data\raw\train.csv)) { New-Item -ItemType Directory -Force data\raw | Out-Null; Copy-Item Train.csv data\raw\train.csv }

# Train model (first time — creates models/production/full_pipeline.pkl)
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
├── backend/              # FastAPI + services
│   └── services/
│       ├── logistics_intelligence.py
│       ├── ai_chat_service.py
│       └── anomaly_service.py
├── frontend/             # Streamlit UI
│   ├── main.py
│   └── views/            # Command center, executive dashboard
├── src/ml_pipeline/      # Training pipeline
├── scripts/
│   ├── train.py
│   ├── monitor_drift.py
│   └── log_prediction.py
├── models/production/    # Trained artifacts (generated locally, not in git)
├── data/raw/             # Place train.csv here
├── docker-compose.yml
├── start.ps1
└── docs/IEEE_HACKATHON_WINNING_PACK.md
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

## Hackathon materials

See **[docs/IEEE_HACKATHON_WINNING_PACK.md](docs/IEEE_HACKATHON_WINNING_PACK.md)** for problem statement, architecture, 3-minute demo script, and judge Q&A.

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
