"""Model evaluation module."""

import pandas as pd
import numpy as np
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                            f1_score, roc_auc_score, confusion_matrix, 
                            classification_report, roc_curve, auc)
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluate model performance."""
    
    def evaluate(self, y_true: pd.Series, y_pred: np.ndarray, 
                y_pred_proba: np.ndarray) -> Dict[str, Any]:
        """Evaluate model.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities
            
        Returns:
            Dictionary with evaluation metrics
        """
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred, zero_division=0),
            'f1_score': f1_score(y_true, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_true, y_pred_proba[:, 1]),
            'confusion_matrix': confusion_matrix(y_true, y_pred),
        }
        
        return metrics
    
    def get_classification_report(self, y_true: pd.Series, y_pred: np.ndarray) -> str:
        """Get classification report.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            
        Returns:
            Classification report as string
        """
        return classification_report(y_true, y_pred, 
                                    target_names=['On Time', 'Delayed'])
    
    def get_feature_importance(self, model) -> pd.DataFrame:
        """Get feature importance.
        
        Args:
            model: Trained model
            
        Returns:
            DataFrame with feature importance
        """
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            feature_names = model.get_booster().feature_names
            
            df_importance = pd.DataFrame({
                'feature': feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False)
            
            return df_importance
        
        return pd.DataFrame()
