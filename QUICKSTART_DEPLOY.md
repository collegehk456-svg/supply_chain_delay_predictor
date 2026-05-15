# SmartShip AI - Quick Deployment Guide

**Last Updated**: May 15, 2026  
**Status**: ✅ Production Ready

---

## 🚀 Deploy in 3 Steps

### Step 1: Prepare (2 minutes)
```bash
# Clone or navigate to project
cd supply-chain-delay-detector

# Copy environment configuration
cp .env.example .env

# Edit configuration (critical: update passwords!)
nano .env
```

### Step 2: Deploy (5 minutes)
```bash
# Using Docker Compose (recommended)
docker-compose build
docker-compose up -d

# Or using deployment script
chmod +x deploy.sh
./deploy.sh
# Select option 1 (Docker Compose)
```

### Step 3: Verify (1 minute)
```bash
# Check services
docker-compose ps

# Test API
curl http://localhost:8000/health

# Access dashboard
open http://localhost:8501
```

---

## ✅ What You Get

After deployment, you have:

### 🔧 Running Services
- **API Server** - http://localhost:8000 (FastAPI)
- **Dashboard** - http://localhost:8501 (Streamlit)
- **Database** - PostgreSQL (port 5432)
- **Cache** - Redis (port 6379)
- **MLflow** - Experiment tracking (http://localhost:5000)

### 📊 Capabilities
- ✅ Real-time shipment delay predictions
- ✅ Batch processing (1000+ shipments)
- ✅ SHAP-based model explanations
- ✅ Generative AI insights
- ✅ Interactive dashboard
- ✅ REST API with full documentation

### 📈 Model Performance
- Accuracy: **65.55%**
- ROC-AUC: **0.7411**
- Inference: **<100ms per prediction**

---

## 📋 Deployment Options

### Option 1: Docker Compose (Full Stack - Recommended)
✅ **Best for**: Production with observability  
⏱️ **Time**: ~5 minutes  
📦 **Includes**: API, Frontend, DB, Cache, MLflow

```bash
docker-compose up -d
```

### Option 2: Docker (Lightweight)
✅ **Best for**: Cloud platforms (AWS, GCP, Azure)  
⏱️ **Time**: ~5 minutes  
📦 **Includes**: API, Frontend only

```bash
docker build -t smartship-api .
docker run -p 8000:8000 smartship-api
```

### Option 3: Native Python
✅ **Best for**: Development & testing  
⏱️ **Time**: ~3 minutes  
📦 **Includes**: API & Frontend (in separate terminals)

```bash
# Terminal 1: API
uvicorn backend.main:app --port 8000

# Terminal 2: Dashboard
streamlit run frontend/main.py
```

---

## 🔗 Service URLs

| Service | URL | Username | Password |
|---------|-----|----------|----------|
| Dashboard | http://localhost:8501 | - | - |
| API | http://localhost:8000 | - | - |
| API Docs | http://localhost:8000/docs | - | - |
| MLflow | http://localhost:5000 | - | - |
| Database | localhost:5432 | supply_chain_user | see .env |
| Cache | localhost:6379 | - | - |

---

## 💡 Quick Commands

### Management
```bash
# View all services
docker-compose ps

# View logs (live)
docker-compose logs -f backend

# Restart a service
docker-compose restart backend

# Stop all services
docker-compose down

# Full cleanup (including data)
docker-compose down -v
```

### Testing
```bash
# Health check
curl http://localhost:8000/health

# Single prediction
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"warehouse_block":"A","mode_of_shipment":"Flight",...}'

# Batch prediction
curl -X POST http://localhost:8000/api/v1/batch_predict \
  -H "Content-Type: application/json" \
  -d '[{...}, {...}]'
```

### Monitoring
```bash
# Check service health
docker-compose exec backend curl http://localhost:8000/health

# View API metrics
curl http://localhost:8000/metrics

# Database status
docker-compose exec postgres pg_isready
```

---

## ⚠️ Important Configuration

### Security (CRITICAL!)
Update these in `.env` before production:

```env
# Database passwords
POSTGRES_PASSWORD=change_me_to_strong_password

# API secret key
SECRET_KEY=generate_with_openssl_rand_hex_32

# Admin key
ADMIN_API_KEY=your_secure_admin_key
```

### Performance
For production, adjust:

```env
# Workers for high load
API_WORKERS=8

# Connection pool
DATABASE_POOL_SIZE=50

# Cache
CACHE_ENABLED=true
REDIS_URL=redis://redis:6379/0
```

### Monitoring
Enable monitoring services:

```env
# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Metrics
PROMETHEUS_ENABLED=true
```

---

## 🐛 Troubleshooting

### "Port 8000 already in use"
```bash
# Find and stop the process
lsof -i :8000
kill -9 <PID>

# Or use different port
docker-compose exec -e API_PORT=8001 backend
```

### "Cannot connect to Docker daemon"
```bash
# Make sure Docker is running
sudo systemctl start docker  # Linux
open -a Docker              # macOS

# Check status
docker ps
```

### "Database connection failed"
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check credentials in .env
cat .env | grep DATABASE

# Restart database
docker-compose restart postgres
docker-compose logs postgres
```

### "Model not found"
```bash
# Check if model exists
ls -la artifacts/full_pipeline.pkl

# Retrain if needed
docker-compose exec backend python scripts/train.py

# Verify
docker-compose exec backend ls -la artifacts/
```

### "Dashboard not connecting to API"
```bash
# Verify API is running
curl http://localhost:8000/health

# Check frontend logs
docker-compose logs frontend

# Check API_URL in frontend config
docker-compose exec frontend echo $API_URL
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [DEPLOYMENT.md](DEPLOYMENT.md) | Detailed deployment guide |
| [PRODUCTION_READY.md](PRODUCTION_READY.md) | Production readiness checklist |
| [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) | Project overview & features |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture |
| [README.md](README.md) | Project details |

---

## 🎯 Next Steps

### 1. Test Locally (5 mins)
```bash
./health_check.sh
```

### 2. Deploy to Development (10 mins)
```bash
docker-compose up -d
# Test all endpoints
# Verify dashboard functionality
```

### 3. Deploy to Staging (30 mins)
```bash
# Update production .env
docker-compose -f docker-compose.yml \
  -f docker-compose.prod.yml up -d
# Run full test suite
# Performance testing
```

### 4. Deploy to Production (60 mins)
```bash
# Final checks
./health_check.sh

# Blue-green deployment
# Monitor closely first 24 hours
# Gradual traffic migration
```

---

## 🔔 Important Notes

⚠️ **Before Production**:
- Update all default passwords in `.env`
- Configure proper SSL/TLS certificates
- Set up monitoring and alerting
- Test backup and restore procedures
- Configure appropriate log retention
- Set up automatic scaling policies

📊 **Monitor These Metrics**:
- API response time (should be < 200ms)
- Error rate (should be < 1%)
- Database connections (should be < 80% of max)
- Memory usage (should be < 80% of available)
- Prediction accuracy (should remain stable)

💾 **Backup Strategy**:
- Daily database backups
- Weekly model artifact backups
- Monthly full system backups
- Test restores monthly

---

## 🆘 Support

- **Documentation**: See DEPLOYMENT.md
- **Logs**: `docker-compose logs -f service_name`
- **Health Check**: `./health_check.sh`
- **API Docs**: http://localhost:8000/docs

---

## ✨ Success Indicators

✅ All services running (`docker-compose ps`)  
✅ Health check passing (`curl http://localhost:8000/health`)  
✅ Dashboard accessible (http://localhost:8501)  
✅ Prediction working (`curl http://localhost:8000/api/v1/predict`)  
✅ No errors in logs (`docker-compose logs`)  

**You're ready to use SmartShip AI!** 🚀

---

**Created**: May 15, 2026  
**Status**: ✅ Production Ready  
**Support**: See documentation files above
