# Supply Chain Delay Predictor - Architecture & Implementation Guide

## 📋 Project Overview

**SmartShip AI** is a production-ready MLOps platform for predicting shipment delays in e-commerce logistics. It combines advanced machine learning with explainability and operational insights.

### Business Problem
- Late deliveries erode customer trust and inflate operational costs
- Ability to predict delays enables proactive interventions (rerouting, prioritization)
- Understanding *why* delays happen is crucial for actionable insights

### Solution Components
1. **Predictive Model**: XGBoost classifier predicting delivery delays
2. **Explainability**: SHAP values explaining individual predictions
3. **REST API**: FastAPI backend for real-time predictions
4. **Dashboard**: Streamlit interactive analytics and monitoring
5. **MLOps**: MLflow experiment tracking, DVC data versioning
6. **DevOps**: Docker containerization, GitHub Actions CI/CD

---

## 🏗️ Improved Project Structure

```
supply_chain_delay_predictor/
├── backend/                          # FastAPI application
│   ├── __init__.py
│   ├── main.py                       # FastAPI app entry point
│   ├── config.py                     # Configuration management
│   ├── dependencies.py               # Dependency injection
│   ├── logging_config.py             # Logging setup
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── health.py            # Health checks
│   │   │   ├── predictions.py       # Prediction endpoints
│   │   │   ├── models.py            # Model management
│   │   │   └── analytics.py         # Analytics endpoints
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── shipment.py          # Shipment request/response models
│   │       └── prediction.py        # Prediction response models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── prediction_service.py    # Prediction logic
│   │   ├── model_service.py         # Model loading/management
│   │   └── explanation_service.py   # SHAP explanations
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── error_handler.py         # Exception handling
│   │   └── logging_middleware.py    # Request/response logging
│   └── utils/
│       ├── __init__.py
│       └── validators.py            # Input validation

├── frontend/                         # Streamlit dashboard
│   ├── __init__.py
│   ├── main.py                       # Streamlit entry point
│   ├── config.py                     # Frontend config
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── home.py                  # Main dashboard
│   │   ├── predictions.py           # Real-time prediction page
│   │   ├── analytics.py             # Analytics & insights
│   │   ├── model_performance.py    # Model metrics & plots
│   │   └── about.py                 # Project info
│   ├── components/
│   │   ├── __init__.py
│   │   ├── charts.py               # Reusable chart components
│   │   ├── metrics.py              # Metric display components
│   │   └── forms.py                # Input forms
│   ├── styles/
│   │   ├── custom.css              # Custom CSS
│   │   └── theme.py                # Streamlit theme config
│   └── utils/
│       ├── __init__.py
│       ├── api_client.py           # API communication
│       └── cache.py                # Caching utilities

├── ml_pipeline/                     # ML components
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py               # Data loading
│   │   ├── validator.py            # Data validation
│   │   ├── preprocessor.py         # Data preprocessing
│   │   └── splitter.py             # Train/test splitting
│   ├── features/
│   │   ├── __init__.py
│   │   ├── engineer.py             # Feature engineering
│   │   ├── transformer.py          # Feature transformations
│   │   └── selector.py             # Feature selection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── trainer.py              # Model training
│   │   ├── evaluator.py            # Model evaluation
│   │   ├── predictor.py            # Prediction wrapper
│   │   └── explainer.py            # SHAP explainability
│   ├── pipeline.py                 # ML pipeline orchestration
│   └── config.py                   # ML config

├── notebooks/                       # Jupyter notebooks for EDA
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_development.ipynb
│   └── 04_evaluation_and_insights.ipynb

├── configs/                         # Configuration files
│   ├── __init__.py
│   ├── default.yaml               # Default configuration
│   ├── development.yaml           # Development environment
│   ├── production.yaml            # Production environment
│   ├── model_config.yaml          # Model hyperparameters
│   └── pipeline_config.yaml       # Pipeline settings

├── data/                           # Data directory
│   ├── raw/                        # Original dataset
│   ├── processed/                  # Processed data
│   ├── features/                   # Engineered features
│   └── predictions/                # Prediction outputs
│   └── .gitkeep

├── models/                         # Trained models
│   ├── production/                 # Production model
│   ├── staging/                    # Staging model
│   ├── archived/                   # Old models
│   └── model_registry.json         # Model metadata

├── tests/                          # Unit & integration tests
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_data_pipeline.py
│   │   ├── test_models.py
│   │   ├── test_validators.py
│   │   └── test_features.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_api_endpoints.py
│   │   ├── test_ml_pipeline.py
│   │   └── test_end_to_end.py
│   └── fixtures/
│       ├── sample_data.py
│       └── mock_models.py

├── docker/                         # Docker configuration
│   ├── Dockerfile.backend          # Backend container
│   ├── Dockerfile.frontend         # Frontend container
│   └── Dockerfile.notebook         # Jupyter notebook container

├── ci_cd/                          # GitHub Actions workflows
│   ├── .github/workflows/
│   │   ├── tests.yml               # Unit & integration tests
│   │   ├── build.yml               # Build Docker images
│   │   ├── deploy.yml              # Deploy to production
│   │   └── model_validation.yml    # Model validation

├── docs/                           # Documentation
│   ├── README.md                   # Main readme
│   ├── ARCHITECTURE.md             # This file
│   ├── API.md                      # API documentation
│   ├── SETUP.md                    # Local setup guide
│   ├── DEPLOYMENT.md               # Deployment guide
│   ├── CONTRIBUTING.md             # Contributing guidelines
│   └── diagrams/
│       ├── architecture.png
│       ├── data_flow.png
│       └── ml_pipeline.png

├── scripts/                        # Utility scripts
│   ├── train.py                    # Training script
│   ├── evaluate.py                 # Model evaluation script
│   ├── predict.py                  # Batch prediction
│   ├── setup_db.py                 # Database setup
│   └── generate_reports.py         # Report generation

├── .gitignore                      # Git ignore rules
├── .github/workflows/              # GitHub Actions workflows
├── .env.example                    # Environment variables template
├── docker-compose.yml              # Multi-container setup
├── requirements.txt                # Python dependencies
├── requirements-dev.txt            # Development dependencies
├── pyproject.toml                  # Project metadata
├── setup.py                        # Package setup
├── pytest.ini                      # Pytest configuration
├── .pre-commit-config.yaml         # Pre-commit hooks
├── dvc.yaml                        # DVC pipeline
├── dvc.lock                        # DVC lock file
├── mlflow_config.yaml              # MLflow configuration
└── README.md                       # Project documentation
```

---

## 🔄 Data Flow Architecture

```
┌─────────────────┐
│  Raw Dataset    │  (Kaggle E-Commerce Shipping Data)
└────────┬────────┘
         │
         ▼
┌────────────────────┐
│  Data Validation   │  (Check schema, types, nulls)
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  Preprocessing     │  (Handle missing values, encoding)
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  Feature Eng.      │  (Create new features)
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  Feature Selection │  (Remove low-importance features)
└────────┬───────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌──────────┐ ┌──────────┐
│ Training │ │ Validation│
│  Set     │ │    Set    │
└────┬─────┘ └──────┬────┘
     │             │
     └──────┬──────┘
            ▼
    ┌─────────────────┐
    │ Model Training  │  (XGBoost, LightGBM, CatBoost)
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  MLflow Tracking│  (Log metrics, params, models)
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │   Evaluation    │  (Precision, Recall, AUC, F1)
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  Model Registry │  (Store production model)
    └────────┬────────┘
             │
    ┌────────┴─────────┐
    ▼                  ▼
┌──────────┐      ┌────────────┐
│ FastAPI  │      │  Streamlit │
│ Backend  │      │ Dashboard  │
└──────────┘      └────────────┘
```

---

## 🚀 ML Pipeline Workflow

### 1. Data Ingestion
- Load Kaggle E-Commerce Shipping Dataset
- Validate data schema and quality
- Handle missing values and outliers

### 2. Exploratory Data Analysis (EDA)
- Statistical summaries
- Distribution analysis
- Correlation analysis
- Outlier detection

### 3. Feature Engineering
**Input Features:**
- Warehouse_block (categorical)
- Mode_of_Shipment (categorical: Ship, Flight, Road)
- Customer_care_calls (numerical)
- Customer_rating (numerical)
- Cost_of_the_Product (numerical)
- Prior_purchases (numerical)
- Product_importance (categorical: Low, Medium, High)
- Gender (categorical)
- Discount_offered (numerical)
- Weight_in_gms (numerical)

**Engineered Features:**
- Customer segment (from prior purchases, ratings)
- Shipment risk score (combination of mode + weight)
- Seasonal indicators (from dates)
- Discount impact score
- Product-mode interaction features
- Log-transformed weight and cost
- Categorical encodings (ordinal, one-hot)

**Target Variable:**
- Reached.on.Time_Y/N (Binary: 0=On time, 1=Delayed)

### 4. Model Training
- Algorithm: XGBoost (primary)
- Alternatives: LightGBM, CatBoost
- Hyperparameter tuning: GridSearchCV, Optuna
- Cross-validation: 5-fold stratified CV
- Class imbalance handling: SMOTE, class weights

### 5. Model Evaluation
- Metrics: Precision, Recall, F1-Score, ROC-AUC, PR-AUC
- Confusion matrix analysis
- Feature importance analysis
- SHAP values for explainability

### 6. Prediction & Explanation
- Real-time predictions via API
- SHAP explanations (why delayed/not delayed?)
- Actionable recommendations
- Confidence scores

---

## 🎯 API Endpoints

### Health & Monitoring
- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /metrics` - System metrics

### Predictions
- `POST /api/v1/predict` - Single prediction
- `POST /api/v1/predict/batch` - Batch predictions
- `POST /api/v1/predict-with-explanation` - Prediction + SHAP explanation

### Model Management
- `GET /api/v1/models` - List available models
- `GET /api/v1/models/active` - Get active model info
- `POST /api/v1/models/switch` - Switch active model

### Analytics
- `GET /api/v1/analytics/summary` - Overall statistics
- `GET /api/v1/analytics/predictions/recent` - Recent predictions
- `GET /api/v1/analytics/feature-importance` - Feature importance

---

## 🔧 Configuration Management

### Environment Variables (.env)
```
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_VERSION=v1

# Model Configuration
MODEL_PATH=models/production/model.pkl
MODEL_THRESHOLD=0.5

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/supply_chain

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=supply_chain_experiments

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Features
FEATURE_STORE_PATH=data/features

# Security
SECRET_KEY=your-secret-key
API_KEY=your-api-key
```

---

## 🐳 Docker Architecture

```
docker-compose.yml
├── backend (FastAPI)      - Port 8000
├── frontend (Streamlit)   - Port 8501
├── mlflow (Tracking)      - Port 5000
├── postgres (Database)    - Port 5432
├── jupyter (Notebooks)    - Port 8888
└── redis (Caching)        - Port 6379
```

---

## 📊 Monitoring & Logging

- **Application Logs**: `logs/app.log`
- **Request Logs**: `logs/requests.log`
- **MLflow Dashboard**: http://localhost:5000
- **API Documentation**: http://localhost:8000/docs
- **Streamlit Dashboard**: http://localhost:8501
- **Prometheus Metrics**: `/metrics` endpoint

---

## 🔐 Security Considerations

1. **API Authentication**: JWT tokens with FastAPI security
2. **Input Validation**: Pydantic models for all inputs
3. **CORS Configuration**: Whitelist trusted domains
4. **Rate Limiting**: Prevent abuse with rate limit middleware
5. **Logging**: No sensitive data in logs
6. **Environment Variables**: Use .env files, never commit secrets

---

## 📈 Model Performance Metrics

### Classification Metrics
- **Precision**: TP / (TP + FP) - Correctness of positive predictions
- **Recall**: TP / (TP + FN) - Coverage of actual positives
- **F1-Score**: Harmonic mean of precision and recall
- **ROC-AUC**: Area under receiver operating characteristic curve
- **PR-AUC**: Area under precision-recall curve

### Business Metrics
- **Cost of False Positives**: Unnecessary interventions
- **Cost of False Negatives**: Missed delay predictions
- **Total Cost Reduction**: From proactive interventions

---

## 🚢 Deployment Options

1. **Local Development**: Docker Compose
2. **Cloud Platforms**: AWS ECS, Google Cloud Run, Azure Container Instances
3. **Kubernetes**: Full container orchestration
4. **Serverless**: AWS Lambda with model endpoints
5. **Traditional Servers**: VM deployment with systemd

---

## 📚 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | FastAPI | REST API, async processing |
| Frontend | Streamlit | Interactive dashboard |
| ML Framework | XGBoost, LightGBM | Classification models |
| Experiment Tracking | MLflow | Model versioning, tracking |
| Data Versioning | DVC | Dataset versioning |
| Database | PostgreSQL | Data persistence |
| Caching | Redis | Performance optimization |
| Containerization | Docker | Reproducible environments |
| CI/CD | GitHub Actions | Automated testing, deployment |
| Testing | pytest | Unit & integration tests |
| Linting | pylint, black | Code quality |
| Monitoring | Prometheus | Metrics collection |
| Documentation | Sphinx | Technical documentation |

---

## 📋 Key Files & Responsibilities

| File | Purpose |
|------|---------|
| `backend/main.py` | FastAPI application entry |
| `frontend/main.py` | Streamlit app entry |
| `ml_pipeline/pipeline.py` | ML pipeline orchestration |
| `configs/default.yaml` | Global configuration |
| `requirements.txt` | Python dependencies |
| `docker-compose.yml` | Multi-container orchestration |
| `.github/workflows/` | CI/CD pipelines |
| `tests/` | Automated tests |
| `docs/` | Documentation |

---

## 🎓 Learning Path

1. **Week 1**: Set up project, exploratory data analysis
2. **Week 2**: Feature engineering, model training
3. **Week 3**: API development, dashboard creation
4. **Week 4**: Testing, deployment, documentation

---

## 🏆 Success Criteria

- ✅ Prediction accuracy > 85%
- ✅ API response time < 100ms
- ✅ 90%+ test coverage
- ✅ Full documentation with diagrams
- ✅ Docker deployable
- ✅ Explainable predictions (SHAP)
- ✅ Actionable recommendations
- ✅ Production-ready code quality

---

*Last Updated: May 2026*
