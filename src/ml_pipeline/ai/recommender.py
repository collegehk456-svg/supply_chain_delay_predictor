"""Action recommendation module using Generative AI."""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class ActionRecommender:
    """Generate actionable recommendations for shipment operations."""
    
    def __init__(self, api_key: str = None, model_name: str = "gemini-pro"):
        """Initialize action recommender.
        
        Args:
            api_key: Google Generative AI API key
            model_name: Model name to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.client = None
        
        if GENAI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel(model_name)
                logger.info(f"Initialized {model_name} for recommendations")
            except Exception as e:
                logger.warning(f"Failed to initialize Generative AI: {e}")
    
    def get_recommendations(self, prediction: int, probability: float,
                           shipment_data: Dict[str, Any],
                           feature_importance: Dict[str, float]) -> List[str]:
        """Get actionable recommendations for a shipment.
        
        Args:
            prediction: Predicted class (0=On Time, 1=Delayed)
            probability: Prediction probability
            shipment_data: Dictionary of shipment details
            feature_importance: Dictionary of feature importance
            
        Returns:
            List of action recommendations
        """
        if self.client:
            return self._get_genai_recommendations(prediction, probability, shipment_data, feature_importance)
        else:
            return self._get_rule_based_recommendations(prediction, probability, shipment_data)
    
    def _get_genai_recommendations(self, prediction: int, probability: float,
                                   shipment_data: Dict[str, Any],
                                   feature_importance: Dict[str, float]) -> List[str]:
        """Get AI-generated recommendations."""
        try:
            prediction_label = "DELAYED" if prediction == 1 else "ON TIME"
            mode = shipment_data.get('Mode_of_Shipment', 'Unknown')
            weight = shipment_data.get('Weight_in_gms', 'Unknown')
            
            prompt = f"Provide 3 actionable supply chain recommendations. Shipment: {prediction_label}, Mode: {mode}, Weight: {weight}g. Be specific and implementable."
            
            response = self.client.generate_content(prompt)
            recommendations = [line.strip() for line in response.text.split('\n') if line.strip()]
            return recommendations
        except Exception as e:
            logger.error(f"GenAI recommendation failed: {e}. Using rule-based.")
            return self._get_rule_based_recommendations(prediction, probability, shipment_data)
    
    def _get_rule_based_recommendations(self, prediction: int, probability: float,
                                       shipment_data: Dict[str, Any]) -> List[str]:
        """Get rule-based recommendations (fallback)."""
        recommendations = []
        
        if prediction == 1:
            recommendations.append("PRIORITY: This shipment is at risk of delay")
            mode = shipment_data.get('Mode_of_Shipment', 'Unknown')
            if mode == 'Ship':
                recommendations.append("Consider expedited shipping via Flight for critical orders")
            recommendations.append("Proactively communicate delays to customer")
        else:
            recommendations.append("Shipment on track for on-time delivery")
            recommendations.append("Standard processing is sufficient")
        
        return recommendations
