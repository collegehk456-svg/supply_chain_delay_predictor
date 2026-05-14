# Deployment Guide

## Production Deployment Options

This guide covers deploying SmartShip AI to production environments.

## 🐳 Docker Deployment

### 1. Build Docker Images
```bash
# Build all images
docker-compose build

# Build specific service
docker build -f docker/Dockerfile.backend -t supply_chain_api:latest .
docker build -f docker/Dockerfile.frontend -t supply_chain_dashboard:latest .
```

### 2. Push to Registry
```bash
# Docker Hub
docker tag supply_chain_api:latest yourusername/supply_chain_api:latest
docker push yourusername/supply_chain_api:latest

# Or private registry
docker tag supply_chain_api:latest registry.example.com/supply_chain_api:latest
docker push registry.example.com/supply_chain_api:latest
```

### 3. Deploy with Docker Compose
```bash
# Copy environment configuration
cp .env.example .env.production
# Edit .env.production with production values

# Start services
docker-compose -f docker-compose.yml \
               --env-file .env.production \
               up -d

# Verify services
docker-compose ps
docker-compose logs -f
```

## ☸️ Kubernetes Deployment

### 1. Create Kubernetes Manifests

**deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: supply-chain-api
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: supply-chain-api
  template:
    metadata:
      labels:
        app: supply-chain-api
    spec:
      containers:
      - name: api
        image: yourusername/supply_chain_api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: supply-chain-api-service
spec:
  selector:
    app: supply-chain-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 2. Deploy to Kubernetes
```bash
# Create namespace
kubectl create namespace supply-chain

# Create secrets
kubectl create secret generic app-secrets \
  --from-literal=database-url=postgresql://user:pass@db:5432/supply_chain \
  -n supply-chain

# Apply manifests
kubectl apply -f k8s/deployment.yaml -n supply-chain
kubectl apply -f k8s/service.yaml -n supply-chain

# Verify deployment
kubectl get pods -n supply-chain
kubectl get svc -n supply-chain
```

## ☁️ AWS Deployment

### Option 1: AWS ECS (Elastic Container Service)

```bash
# 1. Create ECR repositories
aws ecr create-repository --repository-name supply-chain-api
aws ecr create-repository --repository-name supply-chain-dashboard

# 2. Tag and push images
aws ecr get-login-password | docker login --username AWS --password-stdin [account-id].dkr.ecr.us-east-1.amazonaws.com
docker tag supply_chain_api:latest [account-id].dkr.ecr.us-east-1.amazonaws.com/supply-chain-api:latest
docker push [account-id].dkr.ecr.us-east-1.amazonaws.com/supply-chain-api:latest

# 3. Create ECS task definition
# Use AWS Console or create JSON file

# 4. Create ECS service
aws ecs create-service --cluster supply-chain-cluster \
  --service-name supply-chain-api \
  --task-definition supply-chain-api:1 \
  --desired-count 2
```

### Option 2: AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p docker supply-chain-api

# Deploy
eb create supply-chain-prod
eb deploy
```

### Option 3: AWS Lambda + API Gateway

```python
# lambda_handler.py
from mangum import Mangum
from backend.main import app

handler = Mangum(app)
```

```bash
# Package
pip install -r requirements.txt -t package/
cd package && zip -r ../deployment.zip . && cd ..
zip deployment.zip lambda_handler.py

# Deploy
aws lambda create-function \
  --function-name supply-chain-predictor \
  --runtime python3.10 \
  --role arn:aws:iam::ACCOUNT:role/lambda-role \
  --handler lambda_handler.handler \
  --zip-file fileb://deployment.zip
```

## 🔷 Azure Deployment

### Azure Container Instances

```bash
# Create resource group
az group create --name supply-chain-rg --location eastus

# Create container registry
az acr create --resource-group supply-chain-rg \
  --name supplychainregistry --sku Basic

# Build and push image
az acr build --registry supplychainregistry \
  --image supply-chain-api:latest .

# Deploy container
az container create \
  --resource-group supply-chain-rg \
  --name supply-chain-api \
  --image supplychainregistry.azurecr.io/supply-chain-api:latest \
  --ports 8000 \
  --environment-variables \
    DATABASE_URL=postgresql://user:pass@db:5432/supply_chain
```

### Azure App Service

```bash
# Create App Service plan
az appservice plan create \
  --name supply-chain-plan \
  --resource-group supply-chain-rg \
  --sku B2 \
  --is-linux

# Create web app
az webapp create \
  --resource-group supply-chain-rg \
  --plan supply-chain-plan \
  --name supply-chain-app \
  --deployment-container-image-name-user supplychainregistry.azurecr.io/supply-chain-api:latest
```

## 🔒 Security Checklist

- [ ] Change all default passwords
- [ ] Set environment-specific `.env` file
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up API authentication (JWT)
- [ ] Enable CORS only for trusted domains
- [ ] Set up logging and monitoring
- [ ] Regular security audits
- [ ] Database encryption
- [ ] Secret management (AWS Secrets Manager, Azure Key Vault)
- [ ] Rate limiting enabled
- [ ] OWASP security headers configured

## 📊 Monitoring & Logging

### Prometheus Metrics
```python
# Add to backend/main.py
from prometheus_client import Counter, Histogram, generate_latest

PREDICTIONS_COUNTER = Counter('predictions_total', 'Total predictions')
PREDICTION_DURATION = Histogram('prediction_duration_seconds', 'Prediction duration')

@app.get("/metrics")
async def metrics():
    return generate_latest()
```

### ELK Stack (Elasticsearch, Logstash, Kibana)
```yaml
# docker-compose.yml additions
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  environment:
    - discovery.type=single-node
  ports:
    - "9200:9200"

kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
  ports:
    - "5601:5601"
```

### CloudWatch (AWS)
```python
import watchtower
import logging

handler = watchtower.CloudWatchLogHandler()
logging.getLogger().addHandler(handler)
```

## 🔄 Continuous Deployment

### GitHub Actions Workflow
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build and push Docker image
      run: |
        docker build -f docker/Dockerfile.backend -t ${{ secrets.REGISTRY }}/supply-chain-api:${{ github.sha }} .
        docker push ${{ secrets.REGISTRY }}/supply-chain-api:${{ github.sha }}
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/supply-chain-api \
          api=${{ secrets.REGISTRY }}/supply-chain-api:${{ github.sha }}
```

## 📈 Scaling Recommendations

### Horizontal Scaling
- Use load balancer (AWS ALB, Nginx)
- Multiple API instances
- Database read replicas for analytics

### Vertical Scaling
- Increase instance CPU/RAM
- Optimize model serving (ONNX, TensorRT)
- Use GPU for inference

### Caching
- Redis for predictions cache
- CDN for static assets
- Database query caching

## 🔧 Health Checks

### API Health Check
```bash
curl http://localhost:8000/health
```

### Database Health
```bash
psql -h db.example.com -U user -d supply_chain -c "SELECT 1"
```

### Model Health
```bash
# Check model file exists and can be loaded
python -c "import joblib; joblib.load('models/production/model.pkl')"
```

## 🚨 Rollback Procedure

```bash
# Kubernetes rollback
kubectl rollout undo deployment/supply-chain-api

# Docker Compose
docker-compose down
git checkout previous-version
docker-compose up -d

# AWS ECS
aws ecs update-service --cluster supply-chain-cluster \
  --service supply-chain-api \
  --task-definition supply-chain-api:2
```

## 📋 Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Dependencies updated
- [ ] Database migrations tested
- [ ] Secrets configured securely
- [ ] Monitoring setup complete
- [ ] Backup procedures in place
- [ ] Load testing completed
- [ ] Security scan passed
- [ ] Documentation updated
- [ ] Team notified of deployment
- [ ] Rollback plan documented

## 🆘 Troubleshooting

### Container won't start
```bash
docker logs supply_chain_api
docker exec -it supply_chain_api sh
```

### Database connection failed
```bash
# Check connection string
psql "$DATABASE_URL"

# Reset database
python scripts/setup_db.py
```

### Model not loading
```bash
# Check file exists
ls -la models/production/

# Verify model integrity
python -c "import joblib; joblib.load('models/production/model.pkl')"
```

## 📞 Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Review error messages
3. Consult [docs/](docs/) folder
4. Open GitHub issue

---

**Last Updated**: May 2024
