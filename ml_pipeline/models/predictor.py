"""
Model Predictor Module
Handles making predictions with trained models.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
import joblib
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelPredictor:
    """Make predictions with trained models."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize ModelPredictor.
        
        Args:
            model_path: Path to trained model. If None, model should be loaded later.
        """
        self.model = None
        self.model_path = model_path
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def load_model(self, model_path: str) -> None:
        """
        Load trained model from file.
        
        Args:
            model_path: Path to model file
        """
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        self.model = joblib.load(model_path)
        self.model_path = model_path
        logger.info(f"Model loaded from {model_path}")
    
    def predict(
        self,
        X: pd.DataFrame,
        return_proba: bool = False,
    ) -> Dict[str, np.ndarray]:
        """
        Make predictions.
        
        Args:
            X: Input features
            return_proba: Whether to return probabilities
        
        Returns:
            Dictionary with predictions and optionally probabilities
        """
        if self.model is None:
            raise ValueError("No model loaded. Call load_model() first.")
        
        predictions = self.model.predict(X)
        
        result = {'predictions': predictions}
        
        if return_proba:
            probabilities = self.model.predict_proba(X)
            result['probabilities'] = probabilities
        
        return result
    
    def predict_single(self, features: Dict[str, any]) -> Dict[str, any]:
        """
        Make a single prediction from feature dictionary.
        
        Args:
            features: Dictionary of feature names and values
        
        Returns:
            Dictionary with prediction and probability
        """
        X = pd.DataFrame([features])
        result = self.predict(X, return_proba=True)
        
        prediction = result['predictions'][0]
        probabilities = result['probabilities'][0]
        
        return {
            'prediction': int(prediction),
            'probability_on_time': float(probabilities[0]),
            'probability_delayed': float(probabilities[1]),
            'confidence': float(max(probabilities)),
        }
    
    def predict_batch(self, X: pd.DataFrame) -> List[Dict[str, any]]:
        """
        Make batch predictions.
        
        Args:
            X: Input features
        
        Returns:
            List of prediction dictionaries
        """
        result = self.predict(X, return_proba=True)
        predictions = result['predictions']
        probabilities = result['probabilities']
        
        batch_results = []
        for pred, proba in zip(predictions, probabilities):
            batch_results.append({
                'prediction': int(pred),
                'probability_on_time': float(proba[0]),
                'probability_delayed': float(proba[1]),
                'confidence': float(max(proba)),
            })
        
        return batch_results
    
    def predict_with_threshold(
        self,
        X: pd.DataFrame,
        threshold: float = 0.5,
    ) -> np.ndarray:
        """
        Make predictions with custom probability threshold.
        
        Args:
            X: Input features
            threshold: Probability threshold for positive class
        
        Returns:
            Array of predictions
        """
        if self.model is None:
            raise ValueError("No model loaded")
        
        probabilities = self.model.predict_proba(X)
        predictions = (probabilities[:, 1] >= threshold).astype(int)
        
        return predictions
    
    def get_feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """
        Get feature importance from model.
        
        Args:
            top_n: Number of top features to return
        
        Returns:
            DataFrame with feature importance
        """
        if self.model is None:
            raise ValueError("No model loaded")
        
        if not hasattr(self.model, 'feature_importances_'):
            raise ValueError("Model does not have feature_importances_ attribute")
        
        feature_names = getattr(self.model, 'feature_names_in_', None)
        if feature_names is None:
            feature_names = [f'Feature_{i}' for i in range(len(self.model.feature_importances_))]
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': self.model.feature_importances_,
        }).sort_values('importance', ascending=False)
        
        return importance_df.head(top_n)
