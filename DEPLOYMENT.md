# SmartShip AI - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Supply Chain Delay Prediction system in production environments. The project supports multiple deployment strategies:

- **Docker Compose** (Recommended) - Full production stack with PostgreSQL, Redis, MLflow
- **Docker** - Containerized API and Frontend
- **Native Python** - Development/local deployment
- **Cloud** - AWS, GCP, Azure (instructions provided)

---

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows (with WSL2)
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk**: Minimum 10GB free space
- **CPU**: 2+ cores

### Required Software
- **Git** - For cloning repository
- **Python 3.10+** - For native deployment
- **Docker & Docker Compose** - For containerized deployment
- **curl** - For API health checks
- **Git LFS** (optional) - For large file management

---

## Quick Start (Docker Compose - Recommended)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/supply-chain-delay-detector.git
cd supply-chain-delay-detector
```

### 2. Configure Environment
```bash
# Copy example configuration
cp .env.example .env

# Edit with your settings (update credentials, API endpoints, etc.)
nano .env
```

### 3. Deploy
```bash
# Make deployment script executable (Linux/macOS)
chmod +x deploy.sh

# Run deployment
./deploy.sh

# Select option 1 (Docker Compose)
```

### 4. Verify Services
```bash
# Check all services are running
docker-compose ps

# View logs
docker-compose logs -f

# Health check API
curl http://localhost:8000/health
```

### 5. Access Services
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501
- **MLflow**: http://localhost:5000

---

## Deployment Methods

### Method 1: Docker Compose (Production - Recommended)

#### Advantages
✅ Complete production stack (DB, Cache, Monitoring)  
✅ Service orchestration and health checks  
✅ Persistent volumes for data  
✅ Easy scaling and updates  
✅ Isolated dependencies  

#### Setup Steps

**1. Install Docker & Docker Compose**
```bash
# macOS (using Homebrew)
brew install docker docker-compose

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Windows - Use Docker Desktop
# Download from https://www.docker.com/products/docker-desktop
```

**2. Configure Environment**
```bash
cp .env.example .env

# Edit critical variables
nano .env
```

Key variables to update:
```env
# Database (change default passwords!)
POSTGRES_USER=supply_chain_user
POSTGRES_PASSWORD=your_secure_password_here

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5000

# Logging
LOG_LEVEL=INFO
```

**3. Build and Start Services**
```bash
# Build all images
docker-compose build

# Start services (in background)
docker-compose up -d

# Or attach terminal output
docker-compose up

# Initialize database (first time only)
docker-compose exec backend python -m alembic upgrade head
```

**4. Verify Deployment**
```bash
# Check service status
docker-compose ps

# Verify API health
curl http://localhost:8000/health

# View logs
docker-compose logs backend      # API logs
docker-compose logs frontend     # Dashboard logs
docker-compose logs postgres     # Database logs

# Test prediction
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "warehouse_block": "A",
    "mode_of_shipment": "Flight",
    "customer_care_calls": 3,
    "customer_rating": 4.0,
    "cost_of_the_product": 5000.0,
    "prior_purchases": 2,
    "product_importance": "High",
    "gender": "M",
    "discount_offered": 25.0,
    "weight_in_gms": 2500.0
  }'
```

**5. Access Services**
```
Dashboard:     http://localhost:8501
API Docs:      http://localhost:8000/docs
MLflow UI:     http://localhost:5000
Health Check:  http://localhost:8000/health
```

**6. Manage Services**
```bash
# View logs (follow mode)
docker-compose logs -f backend

# Restart a service
docker-compose restart backend

# Stop all services
docker-compose down

# Stop and remove all volumes (careful!)
docker-compose down -v

# Update and redeploy
docker-compose pull
docker-compose up -d
```

---

### Method 2: Docker (API + Frontend Only)

#### Advantages
✅ Lightweight containers  
✅ Easy to deploy on AWS ECS, Google Cloud Run, etc.  
✅ Simple scaling with Kubernetes  

#### Setup Steps

**1. Build Docker Images**
```bash
# Build backend
docker build -t smartship-api:latest -f docker/Dockerfile.backend .

# Build frontend
docker build -t smartship-frontend:latest -f docker/Dockerfile.frontend .
```

**2. Run Containers**
```bash
# Create network
docker network create smartship

# Run API
docker run -d \
  --name smartship-api \
  --network smartship \
  -p 8000:8000 \
  -e API_HOST=0.0.0.0 \
  -e API_PORT=8000 \
  -e LOG_LEVEL=INFO \
  smartship-api:latest

# Run Frontend
docker run -d \
  --name smartship-frontend \
  --network smartship \
  -p 8501:8501 \
  -e API_URL=http://smartship-api:8000 \
  smartship-frontend:latest
```

**3. Verify**
```bash
docker ps
curl http://localhost:8000/health
```

---

### Method 3: Native Python (Development)

#### Advantages
✅ Easy to develop and test locally  
✅ Quick iteration  
✅ Easier debugging  

#### Setup Steps

**1. Create Virtual Environment**
```bash
# Python 3.10+
python -m venv venv

# Activate
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**2. Install Dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure Environment**
```bash
cp .env.example .env
nano .env
```

**4. Train Model (if needed)**
```bash
python scripts/train.py \
  --data-path data/raw/train.csv \
  --output-path artifacts/model.pkl
```

**5. Start Services (in separate terminals)**

Terminal 1 - API Server:
```bash
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

Terminal 2 - Dashboard:
```bash
source venv/bin/activate
streamlit run frontend/main.py
```

Terminal 3 - MLflow (optional):
```bash
source venv/bin/activate
mlflow server --backend-store-uri sqlite:///mlflow.db
```

**6. Access Services**
```
API:        http://localhost:8000
Dashboard:  http://localhost:8501
MLflow:     http://localhost:5000
```

---

## Cloud Deployment

### AWS Deployment

#### Option 1: Elastic Container Service (ECS) with Fargate

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Create ECR repositories
aws ecr create-repository --repository-name smartship-api
aws ecr create-repository --repository-name smartship-frontend

# Push images
docker tag smartship-api:latest YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/smartship-api:latest
docker push YOUR_ACCOUNT.dkr.ecr.REGION.amazonaws.com/smartship-api:latest

# Create ECS task definition (see aws/ecs-task-definition.json)
# Create ECS service
# Deploy load balancer
```

#### Option 2: Elastic Beanstalk

```bash
# Install Elastic Beanstalk CLI
pip install awsebcli

# Initialize
eb init -p docker smartship-api

# Create environment
eb create smartship-prod

# Deploy
eb deploy

# Monitor
eb logs
```

#### Option 3: Lambda + API Gateway

Use for serverless prediction API (for low-traffic scenarios).

---

### Google Cloud Deployment

#### Cloud Run (Recommended)

```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash

# Authenticate
gcloud auth login

# Create project
gcloud projects create smartship-api

# Build and push to Container Registry
gcloud builds submit --tag gcr.io/smartship-api/backend

# Deploy to Cloud Run
gcloud run deploy smartship-api \
  --image gcr.io/smartship-api/backend \
  --platform managed \
  --region us-central1 \
  --port 8000

# Get service URL
gcloud run services describe smartship-api --region us-central1
```

---

### Azure Deployment

#### Container Instances

```bash
# Login to Azure
az login

# Create resource group
az group create --name smartship --location eastus

# Create container registry
az acr create --name smartship --resource-group smartship --sku Basic

# Build and push
az acr build --registry smartship --image smartship-api:latest .

# Deploy
az container create \
  --resource-group smartship \
  --name smartship-api \
  --image smartship.azurecr.io/smartship-api:latest \
  --port 8000 \
  --dns-name-label smartship-api
```

---

## Production Checklist

Before deploying to production, verify:

- [ ] **Environment Variables**
  - [ ] `.env` file configured with secure credentials
  - [ ] Database credentials updated
  - [ ] API keys and tokens set
  - [ ] API_URL points to correct endpoint

- [ ] **Database**
  - [ ] PostgreSQL is running
  - [ ] Database migrations applied
  - [ ] Backups configured
  - [ ] Replication set up (if HA needed)

- [ ] **Security**
  - [ ] SSL/TLS certificates installed
  - [ ] Firewall rules configured
  - [ ] Rate limiting enabled
  - [ ] CORS properly configured
  - [ ] Secrets manager configured

- [ ] **Monitoring**
  - [ ] Health check endpoints working
  - [ ] Logging configured
  - [ ] Metrics collection running
  - [ ] Alerts configured

- [ ] **Performance**
  - [ ] Model inference time < 100ms
  - [ ] API response time acceptable
  - [ ] Database queries optimized
  - [ ] Caching configured

- [ ] **Testing**
  - [ ] Unit tests passing
  - [ ] Integration tests passing
  - [ ] API endpoint tests passing
  - [ ] Load testing done

- [ ] **Backup & Recovery**
  - [ ] Database backups automated
  - [ ] Model versioning configured
  - [ ] Rollback plan documented
  - [ ] Disaster recovery tested

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Docker Memory Issues
```bash
# Increase Docker memory
docker-compose down
# Edit Docker settings (Docker Desktop)
# Increase memory to 4GB+
docker-compose up -d
```

### API Connection Issues
```bash
# Check if API is running
curl http://localhost:8000/health

# Check logs
docker-compose logs backend

# Check network
docker network ls
docker-compose down
docker-compose up -d
```

### Model Not Loading
```bash
# Check artifacts directory
ls -la artifacts/

# Retrain model
docker-compose exec backend python scripts/train.py

# Verify model file
docker-compose exec backend ls -la artifacts/
```

### Dashboard Not Connecting
```bash
# Check API_URL is correct
echo $API_URL

# Check frontend logs
docker-compose logs frontend

# Test API from frontend container
docker-compose exec frontend curl http://backend:8000/health
```

---

## Maintenance

### Regular Tasks

**Daily**
- Monitor error logs
- Check API uptime
- Verify predictions quality

**Weekly**
- Review performance metrics
- Check storage usage
- Update dependencies (if needed)

**Monthly**
- Retrain model with new data
- Audit security logs
- Performance optimization
- Backup verification

**Quarterly**
- Security audit
- Dependency updates
- Capacity planning
- Disaster recovery drill

---

## Performance Tuning

### API Optimization
```yaml
# In configs/default.yaml
api:
  workers: 4  # Increase for more CPU cores
  worker_class: uvicorn.workers.UvicornWorker
  timeout: 60
  max_requests: 1000
```

### Database Optimization
```sql
-- Create indexes
CREATE INDEX idx_shipment_date ON shipments(created_at);
CREATE INDEX idx_status ON shipments(status);

-- Connection pooling
ALTER SYSTEM SET max_connections = 200;
```

### Caching
```python
# Enable Redis caching in backend/main.py
from redis import Redis
redis_client = Redis(host='redis', port=6379)
```

---

## Scaling

### Horizontal Scaling (Multiple Instances)

**Docker Compose with load balancer:**
```yaml
services:
  backend1:
    image: smartship-api
    port: 8001
  backend2:
    image: smartship-api
    port: 8002
  
  nginx:
    image: nginx:latest
    ports:
      - "8000:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

**Kubernetes:**
```bash
kubectl scale deployment smartship-api --replicas=5
```

### Vertical Scaling
- Increase CPU/Memory allocation
- Upgrade database server
- Enable query caching

---

## Monitoring & Logging

### Application Monitoring
```bash
# View logs
docker-compose logs -f --tail=100

# Export logs
docker-compose logs > logs_dump.txt
```

### Health Endpoints
```bash
# API health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/db

# Cache health
curl http://localhost:8000/health/cache
```

### Metrics Collection (Prometheus)
```bash
# Access Prometheus
curl http://localhost:9090

# View metrics
curl http://localhost:8000/metrics
```

---

## Security Hardening

### Network Security
```bash
# Enable UFW firewall (Ubuntu)
sudo ufw enable
sudo ufw allow 22
sudo ufw allow 8000
sudo ufw allow 8501
```

### SSL/TLS
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Update docker-compose.yml to use certificates
```

### Secrets Management
```bash
# Use Docker secrets (production)
echo "your_database_password" | docker secret create db_password -

# Or use AWS Secrets Manager
# Or use HashiCorp Vault
```

---

## Rollback Procedure

If deployment fails:

```bash
# Check recent images
docker image ls

# Roll back to previous version
docker-compose down
docker pull smartship-api:v1.0.0
docker-compose up -d

# Verify
docker-compose ps
curl http://localhost:8000/health
```

---

## Support & Documentation

- **Issues**: GitHub Issues
- **Documentation**: Read the docs
- **Community**: Discussion forum
- **Email**: support@smartship.ai

---

**Last Updated**: May 15, 2026  
**Maintained By**: DevOps Team  
**Next Review**: August 15, 2026
