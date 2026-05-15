#!/bin/bash

################################################################################
# SmartShip AI - Deployment Health Check Script
# Verifies all services are running and functional
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

passed=0
failed=0

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         SmartShip AI - Deployment Health Check                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check a service
check_service() {
    local name=$1
    local url=$2
    local expected_code=$3
    
    echo -n "[*] Checking $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$response" == "$expected_code" ]; then
        echo -e "${GREEN}OK (HTTP $response)${NC}"
        ((passed++))
    else
        echo -e "${RED}FAILED (HTTP $response, expected $expected_code)${NC}"
        ((failed++))
    fi
}

# Function to check Docker containers
check_containers() {
    echo ""
    echo -e "${BLUE}[→] Docker Containers${NC}"
    
    if command -v docker-compose &> /dev/null; then
        echo "[*] Checking Docker Compose services..."
        
        services=$(docker-compose ps --services 2>/dev/null || echo "")
        if [ -z "$services" ]; then
            echo -e "${YELLOW}[!] No services running. Run: docker-compose up -d${NC}"
            return 1
        fi
        
        docker-compose ps | grep -E "^\w|State"
        ((passed++))
    else
        echo -e "${YELLOW}[!] Docker Compose not installed${NC}"
        ((failed++))
    fi
}

# Function to check API
check_api() {
    echo ""
    echo -e "${BLUE}[→] API Endpoints${NC}"
    
    check_service "API Health" "http://localhost:8000/health" "200"
    check_service "API Docs" "http://localhost:8000/docs" "200"
    check_service "OpenAPI Schema" "http://localhost:8000/openapi.json" "200"
}

# Function to test prediction
test_prediction() {
    echo ""
    echo -e "${BLUE}[→] Prediction Testing${NC}"
    
    echo -n "[*] Testing single prediction... "
    
    response=$(curl -s -X POST http://localhost:8000/api/v1/predict \
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
        }' 2>/dev/null)
    
    if echo "$response" | grep -q "prediction"; then
        echo -e "${GREEN}OK${NC}"
        echo "  Response: $response" | head -c 80
        echo ""
        ((passed++))
    else
        echo -e "${RED}FAILED${NC}"
        echo "  Response: $response"
        ((failed++))
    fi
}

# Function to check frontend
check_frontend() {
    echo ""
    echo -e "${BLUE}[→] Frontend Dashboard${NC}"
    
    echo -n "[*] Checking Streamlit... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8501/" 2>/dev/null || echo "000")
    
    if [ "$response" == "200" ] || [ "$response" == "301" ]; then
        echo -e "${GREEN}OK${NC}"
        ((passed++))
    else
        echo -e "${YELLOW}STARTING (Streamlit takes time to start)${NC}"
    fi
}

# Function to check database
check_database() {
    echo ""
    echo -e "${BLUE}[→] Database Connection${NC}"
    
    echo -n "[*] Checking PostgreSQL... "
    
    if command -v pg_isready &> /dev/null; then
        if pg_isready -h localhost -U supply_chain_user -d supply_chain >/dev/null 2>&1; then
            echo -e "${GREEN}OK${NC}"
            ((passed++))
        else
            echo -e "${RED}FAILED - Cannot connect${NC}"
            ((failed++))
        fi
    else
        echo -e "${YELLOW}pg_isready not available (may be in Docker)${NC}"
    fi
}

# Function to check cache
check_cache() {
    echo ""
    echo -e "${BLUE}[→] Cache (Redis)${NC}"
    
    echo -n "[*] Checking Redis... "
    
    if command -v redis-cli &> /dev/null; then
        if redis-cli -h localhost ping >/dev/null 2>&1; then
            echo -e "${GREEN}OK${NC}"
            ((passed++))
        else
            echo -e "${RED}FAILED${NC}"
            ((failed++))
        fi
    else
        echo -e "${YELLOW}redis-cli not available (may be in Docker)${NC}"
    fi
}

# Function to check model artifacts
check_artifacts() {
    echo ""
    echo -e "${BLUE}[→] Model Artifacts${NC}"
    
    artifacts=("artifacts/full_pipeline.pkl" "artifacts/model.pkl" "artifacts/metrics.json")
    
    for artifact in "${artifacts[@]}"; do
        echo -n "[*] Checking $artifact... "
        if [ -f "$artifact" ]; then
            size=$(du -h "$artifact" | cut -f1)
            echo -e "${GREEN}OK ($size)${NC}"
            ((passed++))
        else
            echo -e "${RED}MISSING${NC}"
            ((failed++))
        fi
    done
}

# Function to check dependencies
check_dependencies() {
    echo ""
    echo -e "${BLUE}[→] Python Dependencies${NC}"
    
    python_available=false
    
    if command -v python &> /dev/null; then
        python_available=true
        python_version=$(python --version 2>&1)
    elif command -v python3 &> /dev/null; then
        python_available=true
        python_version=$(python3 --version 2>&1)
    fi
    
    if [ "$python_available" = true ]; then
        echo "[*] $python_version"
        
        required_packages=("fastapi" "streamlit" "xgboost" "pandas" "sklearn")
        
        for package in "${required_packages[@]}"; do
            echo -n "[*] Checking $package... "
            if python -c "import $package" 2>/dev/null; then
                echo -e "${GREEN}OK${NC}"
                ((passed++))
            else
                echo -e "${RED}MISSING${NC}"
                ((failed++))
            fi
        done
    else
        echo -e "${RED}Python not found${NC}"
        ((failed++))
    fi
}

# Function to show summary
show_summary() {
    echo ""
    echo "=" * 80
    echo -e "${BLUE}Health Check Summary${NC}"
    echo "=" * 80
    echo -e "Passed:  ${GREEN}$passed${NC}"
    echo -e "Failed:  ${RED}$failed${NC}"
    echo ""
    
    if [ $failed -eq 0 ]; then
        echo -e "${GREEN}✓ All checks passed! System is ready.${NC}"
        echo ""
        echo "Access points:"
        echo "  Dashboard:  http://localhost:8501"
        echo "  API:        http://localhost:8000"
        echo "  API Docs:   http://localhost:8000/docs"
        echo "  MLflow:     http://localhost:5000"
        return 0
    else
        echo -e "${RED}✗ Some checks failed. See above for details.${NC}"
        echo ""
        echo "Common fixes:"
        echo "  1. Ensure Docker containers are running: docker-compose up -d"
        echo "  2. Check logs: docker-compose logs -f"
        echo "  3. Verify ports are not in use: lsof -i -P"
        return 1
    fi
}

# Run all checks
check_containers
check_api
test_prediction
check_frontend
check_database
check_cache
check_artifacts
check_dependencies

# Show summary
show_summary
