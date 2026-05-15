"""
Shipment Schema Models
Pydantic models for request/response validation.
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator


class ShipmentInput(BaseModel):
    """Input model for shipment prediction."""
    
    warehouse_block: str = Field(..., description="Warehouse location block")
    mode_of_shipment: str = Field(..., description="Shipment mode (Ship, Flight, Road)")
    customer_care_calls: int = Field(
        ..., 
        ge=0, 
        description="Number of customer care calls"
    )
    customer_rating: float = Field(
        ..., 
        ge=1.0, 
        le=5.0, 
        description="Customer rating (1-5)"
    )
    cost_of_the_product: float = Field(..., gt=0, description="Product cost in currency")
    prior_purchases: int = Field(..., ge=0, description="Prior purchase count")
    product_importance: str = Field(
        ..., 
        description="Product importance level (Low, Medium, High)"
    )
    gender: str = Field(..., description="Customer gender")
    discount_offered: float = Field(..., ge=0, le=100, description="Discount percentage")
    weight_in_gms: float = Field(..., gt=0, description="Product weight in grams")
    
    @validator("mode_of_shipment")
    def validate_shipment_mode(cls, v):
        """Validate shipment mode."""
        valid_modes = {"Ship", "Flight", "Road"}
        if v not in valid_modes:
            raise ValueError(f"Shipment mode must be one of {valid_modes}")
        return v
    
    @validator("product_importance")
    def validate_product_importance(cls, v):
        """Validate product importance."""
        valid_importance = {"Low", "Medium", "High"}
        if v not in valid_importance:
            raise ValueError(f"Product importance must be one of {valid_importance}")
        return v
    
    @validator("gender")
    def validate_gender(cls, v):
        """Validate gender."""
        valid_genders = {"M", "F"}
        if v not in valid_genders:
            raise ValueError(f"Gender must be one of {valid_genders}")
        return v
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "warehouse_block": "A",
                "mode_of_shipment": "Flight",
                "customer_care_calls": 3,
                "customer_rating": 4.5,
                "cost_of_the_product": 5000,
                "prior_purchases": 2,
                "product_importance": "High",
                "gender": "M",
                "discount_offered": 15,
                "weight_in_gms": 2500,
            }
        }


class ShipmentPrediction(BaseModel):
    """Shipment prediction response."""
    
    prediction: int = Field(..., description="Prediction (0=On time, 1=Delayed)")
    probability_delayed: float = Field(..., ge=0, le=1, description="Probability of delay")
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence")
    model_version: str = Field(..., description="Model version used")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "prediction": 1,
                "probability_delayed": 0.78,
                "confidence": 0.95,
                "model_version": "v1.0",
            }
        }


class ShipmentExplanation(BaseModel):
    """Prediction explanation response."""
    
    prediction: int = Field(..., description="Prediction (0=On time, 1=Delayed)")
    probability_delayed: float = Field(..., ge=0, le=1)
    top_factors: List[dict] = Field(..., description="Top contributing factors")
    explanation_text: str = Field(..., description="Natural language explanation")
    recommendations: List[str] = Field(..., description="Actionable recommendations")
    model_version: str = Field(..., description="Model version used")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "prediction": 1,
                "probability_delayed": 0.78,
                "top_factors": [
                    {"feature": "Weight_in_gms", "importance": 0.25},
                    {"feature": "Mode_of_Shipment", "importance": 0.20},
                ],
                "explanation_text": "This shipment is likely to be delayed due to high weight and ship mode.",
                "recommendations": [
                    "Consider air transport for faster delivery",
                    "Reduce product weight if possible",
                ],
                "model_version": "v1.0",
            }
        }


class BatchPredictionRequest(BaseModel):
    """Batch prediction request."""
    
    shipments: List[ShipmentInput] = Field(..., description="List of shipments to predict")
    
    class Config:
        """Pydantic config."""
        schema_extra = {
            "example": {
                "shipments": [
                    {
                        "warehouse_block": "A",
                        "mode_of_shipment": "Flight",
                        "customer_care_calls": 3,
                        "customer_rating": 4.5,
                        "cost_of_the_product": 5000,
                        "prior_purchases": 2,
                        "product_importance": "High",
                        "gender": "M",
                        "discount_offered": 15,
                        "weight_in_gms": 2500,
                    }
                ]
            }
        }


class BatchPredictionResponse(BaseModel):
    """Batch prediction response."""
    
    total_predictions: int = Field(..., description="Total predictions made")
    predictions: List[ShipmentPrediction] = Field(..., description="Prediction results")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class OperationalRecommendation(BaseModel):
    """Single operational playbook item."""
    action: str
    impact: str
    priority: str


class BusinessImpact(BaseModel):
    """Estimated financial exposure (USD)."""
    expected_loss_usd: float
    mitigation_savings_usd: float
    priority_escalation_cost_usd: float
    net_benefit_if_action_usd: float


class LogisticsIntelligenceResponse(BaseModel):
    """Full MLOps logistics decision payload."""
    prediction: int
    prediction_label: str
    probability_delayed: float
    confidence: float
    risk_tier: str
    risk_tier_description: str
    priority_score: float
    business_impact: BusinessImpact
    operational_recommendations: List[OperationalRecommendation]
    top_factors: List[dict]
    explanation_text: str
    explainability_method: str
    model_version: str = "v1.0"


class DriftReport(BaseModel):
    """Model / data drift monitoring snapshot."""
    status: str
    delay_rate_baseline: float
    delay_rate_current: Optional[float] = None
    delay_rate_drift: Optional[float] = None
    retrain_recommended: bool
    message: str
    timestamp: str


class HealthStatus(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Status (healthy, degraded, unhealthy)")
    model_loaded: bool = Field(..., description="Is model loaded")
    database_connected: bool = Field(..., description="Is database connected")
    timestamp: str = Field(..., description="Check timestamp")
    version: str = Field(..., description="API version")
