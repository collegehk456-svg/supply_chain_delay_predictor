"""
FastAPI Application
Main entry point for the Supply Chain Delay Prediction API.
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import json

from backend.config import get_config
from backend.logging_config import setup_logging, get_logger
from backend.api.schemas.shipment import (
    ShipmentInput, ShipmentPrediction, ShipmentExplanation,
    BatchPredictionRequest, BatchPredictionResponse, HealthStatus
)
from ml_pipeline.models.predictor import ModelPredictor
from ml_pipeline.models.explainer import SHAPExplainer
from backend.services.recommendation_service import RecommendationService
import joblib
import numpy as np

# Setup logging
config = get_config()
setup_logging(
    log_level=config.get('logging.level', 'INFO'),
    log_file=config.get('logging.file', 'logs/app.log'),
)
logger = get_logger(__name__)

# Global variables
predictor: Optional[ModelPredictor] = None
explainer: Optional[SHAPExplainer] = None
recommendation_service: Optional[RecommendationService] = None
prediction_count = 0


# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown."""
    global predictor, explainer, recommendation_service
    
    # Startup
    logger.info("Starting up application...")
    try:
        model_path = config.get('model.path')
        predictor = ModelPredictor(model_path)
        logger.info("Model loaded successfully")
        
        # Initialize SHAP explainer
        try:
            import pandas as pd
            model = joblib.load('models/production/model.pkl')
            
            # Try to load training data for SHAP background
            try:
                X_train = pd.read_csv('data/processed/X_train.csv')
            except:
                # Fallback: create dummy background with correct dimensions
                X_train = pd.DataFrame(np.random.randn(100, 10))
            
            feature_names = [
                'Warehouse_block', 'Mode_of_Shipment', 'Customer_care_calls',
                'Customer_rating', 'Cost_of_the_Product', 'Prior_purchases',
                'Product_importance', 'Gender', 'Discount_offered', 'Weight_in_gms'
            ]
            
            explainer = SHAPExplainer(model, X_train, feature_names=feature_names)
            logger.info("SHAP explainer initialized successfully")
        except Exception as e:
            logger.warning(f"SHAP initialization failed: {e}. Continuing without SHAP.")
        
        # Initialize recommendation service
        recommendation_service = RecommendationService()
        logger.info("Recommendation service initialized")
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title=config.get('api.title', 'SmartShip AI'),
    description="Supply Chain Delay Prediction API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"]
)


# Exception handler
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    logger.error(f"ValueError: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request, exc):
    """Handle FileNotFoundError exceptions."""
    logger.error(f"FileNotFoundError: {exc}")
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {
        "message": "SmartShip AI - Supply Chain Delay Prediction API",
        "status": "operational",
        "version": "1.0.0",
    }


@app.get("/health", response_model=HealthStatus, tags=["Health"])
async def health_check():
    """Detailed health check."""
    global predictor
    
    return HealthStatus(
        status="healthy" if predictor is not None else "unhealthy",
        model_loaded=predictor is not None,
        database_connected=True,  # Update based on actual DB connection
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
    )


# Prediction endpoints
@app.post("/api/v1/predict", response_model=ShipmentPrediction, tags=["Predictions"])
async def predict(request: ShipmentInput):
    """
    Predict whether a shipment will be delayed.
    
    Args:
        request: Shipment input data
    
    Returns:
        Prediction with confidence score
    """
    global predictor, prediction_count
    
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Prepare data
        import pandas as pd
        X = pd.DataFrame([request.dict()])
        
        # Make prediction
        result = predictor.predict_single(request.dict())
        
        # Log prediction
        prediction_count += 1
        logger.info(f"Prediction {prediction_count}: {result['prediction']}")
        
        return ShipmentPrediction(
            prediction=result['prediction'],
            probability_delayed=result['probability_delayed'],
            confidence=result['confidence'],
            model_version="v1.0",
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/predict/batch", response_model=BatchPredictionResponse, tags=["Predictions"])
async def predict_batch(request: BatchPredictionRequest):
    """
    Make batch predictions for multiple shipments.
    
    Args:
        request: Batch prediction request
    
    Returns:
        Batch predictions with processing time
    """
    global predictor
    
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        import pandas as pd
        import time
        
        start_time = time.time()
        
        # Prepare data
        X = pd.DataFrame([s.dict() for s in request.shipments])
        
        # Make predictions
        results = predictor.predict_batch(X)
        
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        
        predictions = [
            ShipmentPrediction(
                prediction=r['prediction'],
                probability_delayed=r['probability_delayed'],
                confidence=r['confidence'],
                model_version="v1.0",
            )
            for r in results
        ]
        
        logger.info(f"Batch prediction: {len(predictions)} shipments processed in {processing_time:.2f}ms")
        
        return BatchPredictionResponse(
            total_predictions=len(predictions),
            predictions=predictions,
            processing_time_ms=processing_time,
        )
    
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/predict-with-explanation", response_model=ShipmentExplanation, tags=["Predictions"])
async def predict_with_explanation(request: ShipmentInput):
    """
    Predict with natural language explanation and recommendations.
    
    Args:
        request: Shipment input data
    
    Returns:
        Prediction with explanation and recommendations
    """
    global predictor
    
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Get prediction
        result = predictor.predict_single(request.dict())
        
        # Generate explanation
        explanation_text = _generate_explanation(request, result)
        recommendations = _generate_recommendations(request, result)
        
        # Get feature importance
        importance = predictor.get_feature_importance(top_n=5)
        top_factors = [
            {
                "feature": row['feature'],
                "importance": float(row['importance'])
            }
            for _, row in importance.iterrows()
        ]
        
        return ShipmentExplanation(
            prediction=result['prediction'],
            probability_delayed=result['probability_delayed'],
            top_factors=top_factors,
            explanation_text=explanation_text,
            recommendations=recommendations,
            model_version="v1.0",
        )
    
    except Exception as e:
        logger.error(f"Explanation prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/explain", tags=["Explainability"])
async def explain_prediction(request: ShipmentInput):
    """
    Explain a prediction using SHAP values.
    
    Returns:
        - top_factors: Most important features
        - shap_values: SHAP contribution values
        - interpretation: Human-readable explanation
    """
    global predictor, explainer
    
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if explainer is None:
        raise HTTPException(status_code=503, detail="SHAP explainer not initialized")
    
    try:
        # Convert input to feature array in correct order
        feature_array = np.array([[
            _encode_feature(request.warehouse_block, 'warehouse_block'),
            _encode_feature(request.mode_of_shipment, 'mode'),
            request.customer_care_calls,
            request.customer_rating,
            request.cost_of_the_product,
            request.prior_purchases,
            _encode_feature(request.product_importance, 'importance'),
            _encode_feature(request.gender, 'gender'),
            request.discount_offered,
            request.weight_in_gms
        ]])
        
        # Scale features
        scaler = joblib.load('models/production/scaler.pkl')
        X_scaled = scaler.transform(feature_array)
        
        # Get prediction
        prediction_prob = predictor.model.predict_proba(X_scaled)[0][1]
        
        # Get SHAP explanation
        explanation = explainer.explain_single(X_scaled[0])
        
        return {
            "probability_delayed": float(prediction_prob),
            "prediction": int(1 if prediction_prob > 0.5 else 0),
            "top_factors": explanation['top_3_factors'],
            "shap_contributions": [float(v) for v in explanation['top_3_values']],
            "importance_percentages": [float(v) for v in explanation['top_3_importance']],
            "interpretation": f"This shipment has a {prediction_prob*100:.1f}% chance of being delayed. "
                            f"The main drivers are: {', '.join(explanation['top_3_factors'][:2])}"
        }
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/predict/smart", tags=["Predictions"])
async def smart_predict(request: ShipmentInput):
    """
    Complete prediction with explanation and recommendations.
    
    This is the most powerful endpoint - combines:
    1. Prediction
    2. SHAP explanation  
    3. Actionable recommendations
    4. Business impact
    """
    global predictor, explainer, recommendation_service
    
    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if recommendation_service is None:
        raise HTTPException(status_code=503, detail="Recommendation service not initialized")
    
    try:
        # Convert input to feature array
        feature_array = np.array([[
            _encode_feature(request.warehouse_block, 'warehouse_block'),
            _encode_feature(request.mode_of_shipment, 'mode'),
            request.customer_care_calls,
            request.customer_rating,
            request.cost_of_the_product,
            request.prior_purchases,
            _encode_feature(request.product_importance, 'importance'),
            _encode_feature(request.gender, 'gender'),
            request.discount_offered,
            request.weight_in_gms
        ]])
        
        # Scale features
        scaler = joblib.load('models/production/scaler.pkl')
        X_scaled = scaler.transform(feature_array)
        
        # Get prediction
        prediction_prob = float(predictor.model.predict_proba(X_scaled)[0][1])
        prediction = int(1 if prediction_prob > 0.5 else 0)
        
        # Get SHAP explanation
        explanation = None
        top_factors = []
        top_values = []
        if explainer is not None:
            explanation = explainer.explain_single(X_scaled[0])
            top_factors = explanation['top_3_factors']
            top_values = [float(v) for v in explanation['top_3_values']]
        
        # Get recommendations
        recommendations = recommendation_service.generate(
            shipment_data=request.dict(),
            predicted_probability=prediction_prob,
            top_factors=top_factors
        )
        
        return {
            "prediction": prediction,
            "probability_delayed": prediction_prob,
            "confidence": prediction_prob if prediction == 1 else (1.0 - prediction_prob),
            "top_factors": top_factors,
            "shap_contributions": top_values,
            "recommendations": recommendations['recommendations'],
            "estimated_improvement": recommendations['estimated_delay_reduction'],
            "priority_action": recommendations['priority_recommendation']['action'] 
                               if recommendations['priority_recommendation'] else None,
            "business_impact": {
                "current_delay_risk": f"{prediction_prob*100:.1f}%",
                "recommended_actions": len(recommendations['recommendations']),
                "potential_savings": f"${recommendations['total_potential_improvement']*500:.0f}" if recommendations['total_potential_improvement'] > 0 else "$0"
            }
        }
    except Exception as e:
        logger.error(f"Smart prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper function to encode categorical features
def _encode_feature(value, feature_type):
    """Encode categorical features."""
    try:
        encoders = joblib.load('models/production/label_encoders.pkl')
        if feature_type == 'warehouse_block':
            return int(encoders['Warehouse_block'].transform([value])[0])
        elif feature_type == 'mode':
            return int(encoders['Mode_of_Shipment'].transform([value])[0])
        elif feature_type == 'importance':
            return int(encoders['Product_importance'].transform([value])[0])
        elif feature_type == 'gender':
            return int(encoders['Gender'].transform([value])[0])
    except Exception as e:
        logger.warning(f"Feature encoding error for {feature_type}: {e}")
        return 0
    return 0


# Helper functions for explanations
def _generate_explanation(request: ShipmentInput, prediction: dict) -> str:
    """Generate natural language explanation."""
    is_delayed = prediction['prediction'] == 1
    probability = prediction['probability_delayed']
    
    status = "likely to be delayed" if is_delayed else "likely to be on-time"
    confidence = f"{probability*100:.1f}%" if is_delayed else f"{(1-probability)*100:.1f}%"
    
    explanation = f"This shipment is {status} with {confidence} confidence. "
    
    # Add factor-specific explanations
    if request.weight_in_gms > 3000:
        explanation += "The heavy weight may contribute to delays. "
    
    if request.mode_of_shipment == "Ship":
        explanation += "Shipment via sea route typically takes longer. "
    
    if request.discount_offered > 20:
        explanation += "High discounts may indicate promotional shipments with longer processing. "
    
    if request.customer_rating < 3.0:
        explanation += "Low customer ratings suggest potential service issues. "
    
    return explanation


def _generate_recommendations(request: ShipmentInput, prediction: dict) -> list:
    """Generate actionable recommendations."""
    recommendations = []
    
    if request.weight_in_gms > 3000:
        recommendations.append("Consider reducing product weight or packaging to speed up delivery")
    
    if request.mode_of_shipment == "Ship":
        recommendations.append("Switch to air freight for time-critical shipments")
    
    if request.cost_of_the_product > 10000:
        recommendations.append("Use priority handling and tracking for high-value items")
    
    if request.discount_offered > 20:
        recommendations.append("Plan ahead for promotional shipments with longer lead times")
    
    if request.customer_care_calls > 3:
        recommendations.append("Proactively communicate with customer about expected delays")
    
    if request.warehouse_block in ['D', 'E', 'F']:
        recommendations.append("Consider rerouting from remote warehouse blocks")
    
    return recommendations if recommendations else ["Standard delivery processes should be sufficient"]


# Analytics endpoints
@app.get("/api/v1/analytics/summary", tags=["Analytics"])
async def analytics_summary():
    """Get analytics summary."""
    global prediction_count
    
    return {
        "total_predictions": prediction_count,
        "api_status": "operational",
        "model_version": "v1.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/api/v1/models", tags=["Models"])
async def list_models():
    """List available models."""
    return {
        "models": [
            {
                "name": "xgboost_v1.0",
                "status": "active",
                "type": "classification",
            }
        ]
    }


# Error response schema
@app.get("/docs", tags=["Documentation"])
async def get_docs():
    """API Documentation."""
    return {"message": "See /docs for Swagger UI"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.get('api.host', '0.0.0.0'),
        port=config.get('api.port', 8000),
        reload=config.get('api.reload', True),
    )
