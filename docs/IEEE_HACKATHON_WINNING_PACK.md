# IEEE MLOps Hackathon — Supply Chain Delay Predictor
## Winning Pack: SmartShip AI Logistics Intelligence Platform

---

## Standout Project Title

**SmartShip AI — Explainable Delay Intelligence & Autonomous Logistics Control Plane**

*Tagline:* From raw shipment features to risk-tiered decisions, dollar impact, and automated retraining — in one MLOps-native platform.

---

## Problem Statement (Real-World)

Global e-commerce logistics loses **billions annually** to late deliveries. Operations teams see thousands of shipments daily but lack:

- **Early warning** before SLA breach (not just post-mortem reports)
- **Explainable drivers** (why this shipment, not black-box scores)
- **Prioritized intervention** (which 50 shipments to fix first)
- **Business impact** (cost of delay vs cost of expedite)

Our dataset (10,999 shipments) mirrors this: **~60% delayed**, with **discount %** and **weight** as dominant operational levers — matching real promotional surges and heavy-SKU handling bottlenecks.

**We solve:** Predict delay probability → classify risk → explain → recommend → estimate $ impact → monitor drift → retrain — **deployable via API + manager dashboard**.

---

## Three Differentiators (vs Typical Student Projects)

| # | Differentiator | Why Judges Care |
|---|----------------|-----------------|
| 1 | **Decision-grade API** (`/api/v1/predict/logistics`) | Not just `predict()` — returns risk tier, priority score, USD impact, P1/P2 playbooks |
| 2 | **Closed-loop MLOps** | Drift endpoint + prediction logging + `POST /api/v1/mlops/retrain` + MLflow in training |
| 3 | **Operations-first UX** | Command Center + Executive Dashboard + explainability judges can *see* in 30 seconds |

---

## Innovative Feature List (Implemented / Demo-Ready)

- Delay prediction (binary + probability)
- Risk categorization: LOW / MEDIUM / HIGH
- SHAP + natural-language explainability
- Operational recommendation engine (P1/P2/P3 playbooks)
- Shipment prioritization score (0–100)
- Business cost / loss estimation (USD)
- Model drift detection (`GET /api/v1/mlops/drift`)
- Automated retraining trigger (`POST /api/v1/mlops/retrain`)
- FastAPI production API + OpenAPI docs
- Streamlit logistics manager dashboard
- Anomaly detection (Isolation Forest) + live stream
- Multi-agent AI copilot + RAG document upload
- Docker Compose (API, UI, Redis, MLflow, Postgres)
- CI workflows + structured logging

---

## Improved Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Logistics Manager UI (Streamlit)              │
│  Home │ Command Center │ Exec Dashboard │ Predict │ AI Chat      │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST
┌────────────────────────────▼────────────────────────────────────┐
│                     FastAPI Control Plane                          │
│  /predict/logistics │ /predict/batch │ /mlops/drift │ /mlops/retrain│
│  /anomaly/* │ /chat │ /rag/upload                                   │
└─────┬──────────────────┬──────────────────┬─────────────────────┘
      │                  │                  │
┌─────▼─────┐    ┌───────▼────────┐   ┌────▼─────┐
│ XGBoost   │    │ Logistics      │   │ Drift    │
│ Pipeline  │    │ Intelligence   │   │ Monitor  │
│ (22 feat) │    │ Service        │   │ + Logs   │
└───────────┘    └────────────────┘   └──────────┘
      │
┌─────▼──────────────────────────────────────────┐
│ MLOps: train.py → MLflow │ DVC │ metrics.json  │
│ models/production/full_pipeline.pkl             │
└────────────────────────────────────────────────┘
```

---

## End-to-End Folder Structure

```
supply_chain_delay_predictor/
├── backend/                 # FastAPI, services, schemas
│   ├── main.py
│   └── services/
│       ├── logistics_intelligence.py   # NEW: risk, $, priority
│       ├── ai_chat_service.py
│       └── anomaly_service.py
├── frontend/                # Streamlit dashboard
│   ├── main.py
│   └── views/               # command_center, executive_dashboard
├── src/ml_pipeline/           # train, features, SHAP
├── scripts/
│   ├── train.py               # Train + MLflow
│   ├── monitor_drift.py       # Drift + retrain flag
│   └── log_prediction.py
├── models/production/         # full_pipeline.pkl, metrics.json
├── data/raw/train.csv
├── docker-compose.yml
├── .github/workflows/
└── docs/IEEE_HACKATHON_WINNING_PACK.md
```

---

## Best ML Approach

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Model | **XGBoost** | Best tabular performance; fast inference; feature importance |
| Validation | Stratified holdout + CV | Class imbalance (~60% delayed) |
| Metrics | ROC-AUC, F1, Precision | Precision high → trustworthy delay alerts |
| Explainability | SHAP TreeExplainer + rules | Judge-friendly "why" |
| Serving | Single `full_pipeline.pkl` | Preprocess + engineer + predict = reproducible |
| Monitoring | Delay-rate drift vs baseline | Simple, interpretable for ops |

**Current model:** ROC-AUC **0.74**, Precision **0.75** on holdout.

---

## Feature Engineering (From Your Dataset)

| Raw Feature | Engineered Ideas |
|-------------|------------------|
| Discount_offered | `has_discount`, discount bins, interaction with mode |
| Weight_in_gms | `log_weight`, weight_category, weight/cost ratio |
| Cost_of_the_Product | `log_cost`, high-value flag (>$10k) |
| Customer_care_calls | `has_customer_calls`, escalation flag (>3) |
| Mode_of_Shipment | One-hot + delay-rate prior by mode |
| Warehouse_block | Remote block flag (D/E/F) |
| Prior_purchases | New customer flag (<2) |
| Customer_rating | Low rating flag (<3) |
| Product_importance | Ordinal encoding |
| Gender | Low importance (kept for completeness) |

**Key insight for demo:** Discount alone ~**50%** feature importance — tie to promotional surge playbook.

---

## Deployment Plan

1. **Local demo:** `.\start.ps1` → :8501 UI, :8000 API  
2. **Docker:** `docker-compose up` (backend, frontend, MLflow, Redis, Postgres)  
3. **Cloud:** Render/Railway — container + env `API_URL`, `MODEL_PATH`  
4. **CI:** GitHub Actions — test + `python scripts/monitor_drift.py` (fail → retrain job)

---

## Step-by-Step Implementation (What You Run)

```powershell
cd C:\supply_chain_delay_predictor

# 1. Data
# Ensure data/raw/train.csv exists (copy Train.csv if needed)

# 2. Train model + MLflow log
$env:PYTHONPATH = (Get-Location)
python scripts/train.py --data-path data/raw/train.csv --output-path models/production/model.pkl

# 3. Start platform
.\start.ps1

# 4. Demo endpoints
# POST http://localhost:8000/api/v1/predict/logistics
# GET  http://localhost:8000/api/v1/mlops/drift
```

---

## Final Presentation Script (3 Minutes)

**[0:00–0:30] Problem**  
"Logistics managers lose money on preventable delays. We built SmartShip AI — an MLOps control plane that turns shipment features into prioritized, explainable, dollar-quantified actions."

**[0:30–1:30] Live Demo**  
1. Open dashboard — **All Systems Online**  
2. **Single Prediction** — high discount + Ship mode → **HIGH risk**, priority score, **$ expected loss**  
3. Show **SHAP factors** + **P1 playbook** (cap discount / upgrade to Flight)  
4. **Command Center** — live anomaly stream  
5. API docs → `POST /predict/logistics` JSON response  

**[1:30–2:15] MLOps**  
"Training logs to MLflow. Every prediction logs to `logs/prediction_log.csv`. Drift API compares delay-rate vs baseline; retrain endpoint relaunches `train.py`. Docker-ready."

**[2:15–3:00] Impact & Close**  
"74% ROC-AUC on 11K shipments. We don't just predict — we tell ops *what to do* and *what it saves*. SmartShip AI is production-shaped: API, monitoring, retrain loop, executive UI."

---

## Judge Q&A Preparation

**Q: Why XGBoost not deep learning?**  
A: Tabular logistics data; XGBoost wins on accuracy, speed, and interpretability. <50ms inference.

**Q: How do you handle drift?**  
A: We track delay-rate shift vs training baseline; threshold 8%; `GET /mlops/drift` + optional auto-retrain.

**Q: Is the dollar impact real?**  
A: Calibrated assumptions ($85 base penalty, documented in code); adjustable per company. Directionally correct for prioritization.

**Q: Explainability?**  
A: SHAP top factors + rule-based logistics playbooks grounded in feature importance (discount, weight, warehouse).

**Q: Production readiness?**  
A: FastAPI schemas, health checks, Docker Compose, logging, CI, versioned pipeline artifact.

**Q: Class imbalance?**  
A: Stratified split, scale_pos_weight in XGBoost, report precision/recall not accuracy alone.

---

## Future Scalability (Slide Bullet)

- Kafka ingestion for real-time scoring  
- Feature store (Feast) for warehouse/mode aggregates  
- A/B testing delay policies via MLflow Model Registry  
- GPU batch scoring for 1M+ shipments/day  
- Integration with TMS/WMS webhooks  

---

## API Quick Reference (Demo)

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/predict/logistics` | Full intelligence payload |
| `POST /api/v1/predict-with-explanation` | Legacy explain endpoint |
| `GET /api/v1/mlops/drift` | Drift report |
| `POST /api/v1/mlops/retrain?force=false` | Auto-retrain if drift |
| `GET /health` | Model loaded check |

---

*Built for IEEE MLOps Hackathon — incremental upgrade on existing Supply Chain Delay Predictor codebase.*
