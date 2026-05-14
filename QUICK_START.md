# ⚡ Quick Reference Guide

## 🚀 Start Project in 30 Seconds

### Using Docker (Easiest)
```bash
docker-compose up -d
```
✅ Everything runs automatically
- API: http://localhost:8000
- Dashboard: http://localhost:8501

### Using Python (Local Development)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/train.py
```

Then in separate terminals:
```bash
uvicorn backend.main:app --reload --port 8000
streamlit run frontend/main.py
```

---

## 📍 Where Everything Is

| What | Where | Purpose |
|------|-------|---------|
| **API Code** | `backend/main.py` | All REST endpoints |
| **Dashboard** | `frontend/main.py` | Streamlit UI |
| **ML Training** | `scripts/train.py` | Train the model |
| **ML Code** | `ml_pipeline/` | Data, features, models |
| **Configuration** | `configs/default.yaml` | App settings |
| **Tests** | `tests/` | Unit & integration tests |
| **Docker** | `docker-compose.yml` | Container setup |
| **Docs** | `docs/` | Complete documentation |

---

## 🔗 Important URLs (When Running)

```
API          → http://localhost:8000
API Docs     → http://localhost:8000/docs
Dashboard    → http://localhost:8501
MLflow       → http://localhost:5000
Database     → localhost:5432
Cache        → localhost:6379
```

---

## 📊 API Endpoints

### Predictions
```bash
POST /api/v1/predict                      # Single prediction
POST /api/v1/predict/batch                # Multiple predictions
POST /api/v1/predict-with-explanation     # Prediction + explanation
```

### Models
```bash
GET  /api/v1/models                       # List models
GET  /api/v1/models/active                # Get active model
```

### Analytics
```bash
GET  /api/v1/analytics/summary            # Statistics
GET  /health                              # Health check
```

---

## 🧪 Testing

```bash
# All tests
pytest tests/ -v --cov=backend,ml_pipeline

# Quick test
pytest tests/unit -v

# With coverage report
pytest tests/ --cov --cov-report=html
open htmlcov/index.html
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
lsof -i :8000          # Find process
kill -9 <PID>          # Kill it
```

### Model Not Found
```bash
python scripts/train.py # Retrain model
```

### Database Error
```bash
docker-compose restart postgres
```

### Clear Everything
```bash
docker-compose down -v
docker-compose up -d
```

---

## 🎯 Common Tasks

### Make a Prediction
```python
import requests

response = requests.post('http://localhost:8000/api/v1/predict', json={
    "warehouse_block": "A",
    "mode_of_shipment": "Flight",
    "customer_care_calls": 3,
    "customer_rating": 4.5,
    "cost_of_the_product": 5000,
    "prior_purchases": 2,
    "product_importance": "High",
    "gender": "M",
    "discount_offered": 15,
    "weight_in_gms": 2500
})
print(response.json())
```

### Format Code
```bash
black .
flake8 .
```

### Check Logs
```bash
docker-compose logs -f backend
tail -f logs/app.log
```

### Reset Database
```bash
python scripts/setup_db.py
```

---

## 📁 Directory Tree

```
📦 project/
 ├── 🔙 backend/          → FastAPI server
 ├── 🎨 frontend/         → Streamlit dashboard
 ├── 🤖 ml_pipeline/      → Model code
 ├── 📔 notebooks/        → Jupyter notebooks
 ├── 📊 configs/          → Configuration
 ├── 📦 data/             → Datasets
 ├── 🏆 models/           → Trained models
 ├── 🧪 tests/            → Test suite
 ├── 🐳 docker/           → Docker files
 ├── 📚 docs/             → Documentation
 ├── 🚀 scripts/          → Training scripts
 ├── 📄 requirements.txt  → Dependencies
 ├── 🐳 docker-compose.yml → Orchestration
 └── 📖 README.md         → Overview
```

---

## 📖 Read This First

1. **[README.md](README.md)** - Project overview
2. **[SETUP.md](docs/SETUP.md)** - Local setup
3. **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - How it works
4. **[API.md](docs/API.md)** - API reference
5. **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deploy to prod

---

## 🚀 Production Deployment

### Docker
```bash
docker build -f docker/Dockerfile.backend -t api:latest .
docker build -f docker/Dockerfile.frontend -t dashboard:latest .
docker push api:latest
docker push dashboard:latest
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

### AWS
```bash
# See DEPLOYMENT.md for full instructions
aws ecr create-repository --repository-name supply-chain
# ... more commands
```

---

## ✨ Features

| Feature | Status | Where |
|---------|--------|-------|
| ML Model | ✅ Ready | `ml_pipeline/models/` |
| API | ✅ Ready | `backend/main.py` |
| Dashboard | ✅ Ready | `frontend/main.py` |
| Docker | ✅ Ready | `docker/` |
| Tests | ⏳ Ready to create | `tests/conftest.py` |
| Monitoring | 🔜 Next | `logs/` |
| Security | 🔜 Next | Add auth tokens |

---

## 🎓 Learning Path

1. **Understand** - Read [ARCHITECTURE.md](docs/ARCHITECTURE.md)
2. **Setup** - Follow [SETUP.md](docs/SETUP.md)
3. **Explore** - Use the dashboard at localhost:8501
4. **Develop** - Check out `backend/main.py` and `ml_pipeline/`
5. **Deploy** - Read [DEPLOYMENT.md](docs/DEPLOYMENT.md)

---

## 💡 Pro Tips

- 💾 Always use `.env` for secrets (don't commit)
- 🧪 Run tests before committing
- 📝 Check logs in `logs/app.log`
- 🔄 Use `docker-compose` for full environment
- 🐍 Use virtual environment for Python
- 📚 Check docs before asking questions
- 🚀 Deploy to staging before production

---

## 🆘 Need Help?

1. **Check logs**: `docker-compose logs -f`
2. **Read docs**: See `docs/` folder
3. **Browse API**: http://localhost:8000/docs
4. **Check code**: Well-commented and structured
5. **GitHub Issues**: Open an issue

---

## 📞 Contact & Support

- 📧 Email: your-email@example.com
- 🐙 GitHub: [Repository](https://github.com)
- 💬 Discussions: [GitHub Discussions](https://github.com)

---

**Ready to start? Run:** `docker-compose up -d` 🚀

