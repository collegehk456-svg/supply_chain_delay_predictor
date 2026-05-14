# Local Development Setup Guide

## 📋 Prerequisites

- Python 3.10 or higher
- Git
- Docker & Docker Compose (optional, for containerized development)
- PostgreSQL 15 (or use Docker version)
- Redis (or use Docker version)

## 🚀 Quick Start (5 minutes)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/supply_chain_delay_predictor.git
cd supply_chain_delay_predictor
```

### 2. Setup Python Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# For local development, defaults should work fine
```

### 5. Create Necessary Directories
```bash
mkdir -p data/raw data/processed data/features
mkdir -p models/production models/staging
mkdir -p logs
```

## 🐳 Docker Development Setup (Recommended)

### Using Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### What's Running:
- **Backend API**: http://localhost:8000
- **Frontend Dashboard**: http://localhost:8501
- **MLflow**: http://localhost:5000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Jupyter**: http://localhost:8888

## 🏃 Manual Development Setup

### 1. Start PostgreSQL (if not using Docker)
```bash
# Windows (using WSL)
sudo service postgresql start

# macOS
brew services start postgresql@15

# Verify connection
psql -U postgres
```

### 2. Create Database
```bash
createdb supply_chain
```

### 3. Start Redis (if not using Docker)
```bash
# Windows (using WSL)
redis-server

# macOS
brew services start redis
```

### 4. Train the Model
```bash
python scripts/train.py --data-path data/raw/train.csv --output-path models/production/model.pkl
```

If you don't have training data, the script will create sample data automatically.

### 5. Start MLflow Server (in one terminal)
```bash
mlflow server --host 0.0.0.0 --port 5000
```

### 6. Start Backend API (in another terminal)
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 7. Start Frontend Dashboard (in another terminal)
```bash
streamlit run frontend/main.py --server.port 8501
```

### 8. Access the Application
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501
- **MLflow**: http://localhost:5000

## 📊 Working with Jupyter Notebooks

Start Jupyter server:
```bash
jupyter notebook --notebook-dir=notebooks
```

### Available Notebooks:
1. `01_exploratory_data_analysis.ipynb` - EDA and data exploration
2. `02_feature_engineering.ipynb` - Feature creation and engineering
3. `03_model_development.ipynb` - Model training and tuning
4. `04_evaluation_and_insights.ipynb` - Model evaluation and insights

## 🧪 Running Tests

### Unit Tests
```bash
pytest tests/unit -v --cov=backend,ml_pipeline
```

### Integration Tests
```bash
pytest tests/integration -v
```

### All Tests
```bash
pytest tests/ -v --cov=backend,ml_pipeline --cov-report=html
```

Open `htmlcov/index.html` to view coverage report.

## 🔧 Development Tools

### Code Formatting
```bash
black backend/ ml_pipeline/ frontend/
```

### Linting
```bash
flake8 backend/ ml_pipeline/
```

### Type Checking
```bash
mypy backend/ ml_pipeline/ --ignore-missing-imports
```

### Run All Quality Checks
```bash
black .
flake8 .
mypy . --ignore-missing-imports
pytest tests/
```

## 📝 Common Development Tasks

### Generate New API Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Reset Database
```bash
# Docker
docker-compose down -v
docker-compose up -d postgres

# Manual
psql -U postgres -c "DROP DATABASE IF EXISTS supply_chain;"
psql -U postgres -c "CREATE DATABASE supply_chain;"
```

### Clear Cache
```bash
redis-cli FLUSHALL
```

### View Logs
```bash
tail -f logs/app.log
```

### Reload Configuration
Edit `.env` and restart the services.

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port 8000
lsof -i :8000
kill -9 <PID>
```

### Database Connection Error
```bash
# Check PostgreSQL is running
psql -U postgres -c "\l"

# Reset connection
docker-compose restart postgres
```

### Model Not Loading
```bash
# Check model file exists
ls -la models/production/

# Retrain model
python scripts/train.py
```

### Memory Issues
```bash
# Reduce batch size in config
# Reduce number of workers
# Use subset of data for testing
```

### Permission Errors
```bash
# Fix file permissions
chmod -R u+rwx logs/ models/ data/
```

## 📚 Additional Resources

- [API Documentation](API.md)
- [Architecture Guide](ARCHITECTURE.md)
- [Deployment Guide](DEPLOYMENT.md)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Streamlit Docs](https://docs.streamlit.io)
- [XGBoost Docs](https://xgboost.readthedocs.io)

## 🤝 Getting Help

- Check logs in `logs/app.log`
- Review error messages in terminal
- Open an issue on GitHub
- Check existing documentation

---

**Happy Developing! 🚀**
