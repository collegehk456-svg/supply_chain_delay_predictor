#!/bin/bash

################################################################################
# SmartShip AI - Deployment Script
# Deploys the complete Supply Chain Delay Prediction system
# Supports: Docker Compose (recommended), Docker, and Native Python
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${PROJECT_DIR}/.env"
ENV_EXAMPLE="${PROJECT_DIR}/.env.example"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         SmartShip AI - Supply Chain Delay Predictor             ║${NC}"
echo -e "${BLUE}║                    Deployment Script                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to create .env file if it doesn't exist
setup_env_file() {
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}[*] Creating .env file from example...${NC}"
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        echo -e "${GREEN}[✓] .env file created. Update it with your configuration.${NC}"
        echo -e "${YELLOW}[!] Please review .env before deploying:${NC}"
        echo -e "    - Database credentials"
        echo -e "    - API endpoints"
        echo -e "    - Security tokens"
        echo ""
    else
        echo -e "${GREEN}[✓] .env file exists${NC}"
    fi
}

# Function to validate Docker installation
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}[✗] Docker is not installed${NC}"
        echo -e "${YELLOW}Install Docker from https://www.docker.com/products/docker-desktop${NC}"
        exit 1
    fi
    echo -e "${GREEN}[✓] Docker is installed ($(docker --version))${NC}"
}

# Function to validate Docker Compose
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}[✗] Docker Compose is not installed${NC}"
        echo -e "${YELLOW}Install Docker Compose from https://docs.docker.com/compose/install/${NC}"
        exit 1
    fi
    echo -e "${GREEN}[✓] Docker Compose is installed ($(docker-compose --version))${NC}"
}

# Function to deploy with Docker Compose (recommended)
deploy_docker_compose() {
    echo ""
    echo -e "${BLUE}[→] Starting deployment with Docker Compose...${NC}"
    
    check_docker
    check_docker_compose
    setup_env_file
    
    echo ""
    echo -e "${BLUE}[→] Building containers...${NC}"
    docker-compose -f docker-compose.yml build
    
    echo ""
    echo -e "${BLUE}[→] Starting services...${NC}"
    docker-compose -f docker-compose.yml up -d
    
    echo ""
    echo -e "${BLUE}[→] Waiting for services to be ready...${NC}"
    sleep 10
    
    echo ""
    echo -e "${YELLOW}[*] Checking service health...${NC}"
    
    # Check API
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}[✓] API is running at http://localhost:8000${NC}"
    else
        echo -e "${RED}[✗] API health check failed${NC}"
    fi
    
    # Check Frontend
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        echo -e "${GREEN}[✓] Dashboard is running at http://localhost:8501${NC}"
    else
        echo -e "${YELLOW}[*] Dashboard is starting...${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              Deployment Complete - Services Running            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Services:${NC}"
    echo -e "  API:           http://localhost:8000"
    echo -e "  API Docs:      http://localhost:8000/docs"
    echo -e "  Dashboard:     http://localhost:8501"
    echo -e "  MLflow:        http://localhost:5000"
    echo -e "  Database:      localhost:5432"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo -e "  View logs:     docker-compose logs -f backend"
    echo -e "  Stop services: docker-compose down"
    echo -e "  Stop & remove: docker-compose down -v"
    echo ""
}

# Function to deploy with native Python
deploy_native() {
    echo ""
    echo -e "${BLUE}[→] Starting deployment with Native Python...${NC}"
    
    setup_env_file
    
    if [ ! -d "venv" ]; then
        echo -e "${BLUE}[→] Creating virtual environment...${NC}"
        python -m venv venv
    fi
    
    echo -e "${BLUE}[→] Activating virtual environment...${NC}"
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate
    
    echo -e "${BLUE}[→] Installing dependencies...${NC}"
    pip install -q -r requirements.txt
    
    echo -e "${BLUE}[→] Training model (if needed)...${NC}"
    if [ ! -f "artifacts/full_pipeline.pkl" ]; then
        python scripts/train.py --data-path data/raw/train.csv --output-path artifacts/model.pkl
    fi
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║            Setup Complete - Ready to Start Services            ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Start services (in separate terminals):${NC}"
    echo ""
    echo -e "  Terminal 1 - API Server:"
    echo -e "    source venv/bin/activate"
    echo -e "    uvicorn backend.main:app --reload --port 8000"
    echo ""
    echo -e "  Terminal 2 - Dashboard:"
    echo -e "    source venv/bin/activate"
    echo -e "    streamlit run frontend/main.py"
    echo ""
}

# Function to show menu
show_menu() {
    echo ""
    echo -e "${BLUE}Choose deployment method:${NC}"
    echo "  1) Docker Compose (Recommended - includes DB, Redis, MLflow)"
    echo "  2) Docker (API + Frontend only)"
    echo "  3) Native Python (Development environment)"
    echo "  4) Exit"
    echo ""
}

# Main menu
while true; do
    show_menu
    read -p "Select option (1-4): " choice
    
    case $choice in
        1)
            deploy_docker_compose
            break
            ;;
        2)
            echo -e "${YELLOW}[*] Docker deployment option not fully implemented${NC}"
            echo -e "${YELLOW}[*] Use Docker Compose for full production setup${NC}"
            ;;
        3)
            deploy_native
            break
            ;;
        4)
            echo -e "${BLUE}Exiting...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option. Please try again.${NC}"
            ;;
    esac
done
