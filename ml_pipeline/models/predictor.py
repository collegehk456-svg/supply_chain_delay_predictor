"""Prediction module."""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ModelPredictor:
    """Make predictions with trained model."""
    
    def __init__(self, model):
        """Initialize predictor.
        
        Args:
            model: Trained model
        """
        self.model = model
    
    def predict(self, X: pd.DataFrame, threshold: float = 0.5) -> np.ndarray:
        """Make predictions.
        
        Args:
            X: Input features
            threshold: Classification threshold
            
        Returns:
            Predicted labels
        """
        proba = self.model.predict_proba(X)[:, 1]
        return (proba >= threshold).astype(int)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get prediction probabilities.
        
        Args:
            X: Input features
            
        Returns:
            Predicted probabilities
        """
        return self.model.predict_proba(X)
    
    def predict_with_confidence(self, X: pd.DataFrame, threshold: float = 0.5):
        """Make predictions with confidence scores.
        
        Args:
            X: Input features
            threshold: Classification threshold
            
        Returns:
            Tuple of (predictions, confidence)
        """
        proba = self.model.predict_proba(X)
        predictions = (proba[:, 1] >= threshold).astype(int)
        confidence = np.max(proba, axis=1)
        
        return predictions, confidence
