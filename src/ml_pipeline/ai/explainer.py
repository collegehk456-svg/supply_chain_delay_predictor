"""Explainability module using Generative AI."""

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
    logger.warning("google-generativeai not installed. Install with: pip install google-generativeai")


class ExplanationGenerator:
    """Generate natural language explanations for predictions using Generative AI."""
    
    def __init__(self, api_key: str = None, model_name: str = "gemini-pro"):
        """Initialize explanation generator.
        
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
                logger.info(f"Initialized {model_name} for explanations")
            except Exception as e:
                logger.warning(f"Failed to initialize Generative AI: {e}")
                logger.info("Falling back to rule-based explanations")
    
    def generate_explanation(self, prediction: int, probability: float,
                            feature_values: Dict[str, Any],
                            feature_importance: Dict[str, float]) -> str:
        """Generate explanation for a prediction.
        
        Args:
            prediction: Predicted class (0=On Time, 1=Delayed)
            probability: Prediction probability
            feature_values: Dictionary of feature values
            feature_importance: Dictionary of feature importance scores
            
        Returns:
            Natural language explanation
        """
        if self.client:
            return self._generate_with_genai(prediction, probability, feature_values, feature_importance)
        else:
            return self._generate_rule_based(prediction, probability, feature_values, feature_importance)
    
    def _generate_with_genai(self, prediction: int, probability: float,
                             feature_values: Dict[str, Any],
                             feature_importance: Dict[str, float]) -> str:
        """Generate explanation using Generative AI."""
        try:
            prediction_label = "DELAYED" if prediction == 1 else "ON TIME"
            
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            feature_context = "\\n".join([f"- {feat}: importance={imp:.2f}, value={feature_values.get(feat, 'N/A')}" 
                                        for feat, imp in top_features])
            
            prompt = f"Analyze this shipment: Prediction={prediction_label}, Confidence={probability*100:.1f}%. Top factors: {feature_context}. Brief 2-3 sentence explanation."
            
            response = self.client.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"GenAI generation failed: {e}. Using rule-based.")
            return self._generate_rule_based(prediction, probability, feature_values, feature_importance)
    
    def _generate_rule_based(self, prediction: int, probability: float,
                            feature_values: Dict[str, Any],
                            feature_importance: Dict[str, float]) -> str:
        """Generate rule-based explanation (fallback)."""
        prediction_label = "DELAYED" if prediction == 1 else "ON TIME"
        confidence = probability * 100
        
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
        
        explanation = f"Prediction: {prediction_label} (Confidence: {confidence:.1f}%)\n\nKey Factors:\n"
        
        for feat, importance in top_features:
            value = feature_values.get(feat, 'N/A')
            explanation += f"• {feat}: {value} (Importance: {importance:.2%})\n"
        
        if prediction == 1:
            explanation += "\nThis shipment is likely to be delayed. Consider prioritization or rerouting."
        else:
            explanation += "\nThis shipment is predicted to arrive on time. Standard processing is sufficient."
        
        return explanation
