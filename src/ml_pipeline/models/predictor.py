"""Prediction module."""

import pandas as pd
import numpy as np
import logging
import joblib
from typing import Dict, Any, List

from ml_pipeline.data.preprocessor import DataPreprocessor
from ml_pipeline.features.engineer import FeatureEngineer

logger = logging.getLogger(__name__)


class ModelPredictor:
    """Encapsulates the complete prediction pipeline including preprocessing and feature engineering."""
    
    def __init__(self, preprocessor: DataPreprocessor, engineer: FeatureEngineer, model: Any):
        """Initialize predictor with preprocessor, feature engineer, and trained model.
        
        Args:
            preprocessor: Trained DataPreprocessor instance
            engineer: Trained FeatureEngineer instance
            model: Trained model object (e.g., XGBoostClassifier)
        """
        self.preprocessor = preprocessor
        self.engineer = engineer
        self.model = model
        logger.info("ModelPredictor initialized with preprocessor, engineer, and model.")
    
    def _transform_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Apply preprocessing and feature engineering to raw data."""
        raw_data = raw_data.copy()
        raw_data.columns = [col.replace('.', '_').replace('/', '_') for col in raw_data.columns]

        # Map lower-case feature names from API/CLI inputs to training feature names
        feature_cols = (self.preprocessor.numerical_cols or []) + (self.preprocessor.categorical_cols or [])
        rename_map = {feature.lower(): feature for feature in feature_cols}
        raw_data.columns = [rename_map.get(col.lower(), col) for col in raw_data.columns]

        # Apply preprocessing (scaling, encoding)
        processed_data = self.preprocessor.preprocess(raw_data, is_fit=False, handle_outliers=False, scale=True, encode_categorical=True)
        # Apply feature engineering
        engineered_data = self.engineer.engineer_features(processed_data.copy())

        return engineered_data
    
    def predict_single(self, raw_data_dict: Dict[str, Any], threshold: float = 0.5) -> Dict[str, Any]:
        """Make a single prediction with confidence.
        
        Args:
            raw_data_dict: Dictionary of raw input features for a single shipment.
            threshold: Classification threshold
            
        Returns:
            Dictionary containing prediction, probability, and confidence.
        """
        raw_df = pd.DataFrame([raw_data_dict])
        transformed_df = self._transform_data(raw_df)
        
        proba = self.model.predict_proba(transformed_df)[:, 1]
        prediction = int(proba[0] >= threshold)
        confidence = float(proba[0] if prediction == 1 else 1.0 - proba[0])
        
        return {
            "prediction": prediction,
            "probability_delayed": float(proba[0]),
            "confidence": confidence,
        }
    
    def predict_batch(self, raw_data_df: pd.DataFrame, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Make batch predictions with confidence.
        
        Args:
            raw_data_df: DataFrame of raw input features for multiple shipments.
            threshold: Classification threshold
            
        Returns:
            List of dictionaries, each containing prediction, probability, and confidence.
        """
        transformed_df = self._transform_data(raw_data_df)
        
        proba = self.model.predict_proba(transformed_df)[:, 1]
        predictions = (proba >= threshold).astype(int)
        
        results = []
        for i in range(len(predictions)):
            pred = predictions[i]
            prob_delayed = proba[i]
            conf = np.max([prob_delayed, 1 - prob_delayed])
            results.append({
                "prediction": int(pred),
                "probability_delayed": float(prob_delayed),
                "confidence": float(conf),
            })
        return results
    
    def get_feature_importance(self, top_n: int = 5) -> pd.DataFrame:
        """Get feature importance from the trained model."""
        if hasattr(self.model, 'feature_importances_'):
            feature_names = self.model.get_booster().feature_names if hasattr(self.model, 'get_booster') and self.model.get_booster() is not None else []
            if not feature_names:
                logger.warning("Could not get feature names from model booster. Feature importance might be misaligned.")
                # Fallback: try to get feature names from preprocessor's final features
                # This is a heuristic and might not be perfectly accurate if feature engineering is complex
                if hasattr(self.preprocessor, 'final_feature_names') and self.preprocessor.final_feature_names:
                    feature_names = self.preprocessor.final_feature_names
                else:
                    # Last resort: dummy names
                    feature_names = [f"feature_{i}" for i in range(len(self.model.feature_importances_))]
            
            importance = self.model.feature_importances_
            
            df_importance = pd.DataFrame({
                'feature': feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False)
            
            return df_importance.head(top_n)
        
        return pd.DataFrame()
    
    def save(self, filepath: str) -> None:
        """Save the complete ModelPredictor pipeline."""
        joblib.dump(self, filepath)
        logger.info(f"Complete ModelPredictor pipeline saved to {filepath}")
    
    @staticmethod
    def load(filepath: str) -> 'ModelPredictor':
        """Load the complete ModelPredictor pipeline."""
        predictor = joblib.load(filepath)
        logger.info(f"Complete ModelPredictor pipeline loaded from {filepath}")
        return predictor
