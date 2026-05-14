"""
Model Evaluation Module
Handles model evaluation and metrics calculation.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Tuple
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, precision_recall_curve, auc
)
import json

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluate model performance."""
    
    def __init__(self):
        """Initialize ModelEvaluator."""
        self.metrics: Dict[str, Any] = {}
        self.confusion_matrix_data: Dict[str, int] = {}
    
    def evaluate(
        self,
        y_true: pd.Series,
        y_pred: np.ndarray,
        y_pred_proba: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate model predictions.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities (optional)
        
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info("Evaluating model performance")
        
        # Classification metrics
        self.metrics = {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision': float(precision_score(y_true, y_pred, zero_division=0)),
            'recall': float(recall_score(y_true, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_true, y_pred, zero_division=0)),
        }
        
        # Confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        self.confusion_matrix_data = {
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'true_positives': int(tp),
        }
        
        # Add to metrics
        self.metrics.update({
            'confusion_matrix': self.confusion_matrix_data,
            'sensitivity': float(tp / (tp + fn)) if (tp + fn) > 0 else 0,
            'specificity': float(tn / (tn + fp)) if (tn + fp) > 0 else 0,
        })
        
        # Probability-based metrics
        if y_pred_proba is not None:
            try:
                self.metrics['roc_auc'] = float(roc_auc_score(y_true, y_pred_proba[:, 1]))
                
                # Precision-Recall AUC
                precision, recall, _ = precision_recall_curve(y_true, y_pred_proba[:, 1])
                pr_auc = auc(recall, precision)
                self.metrics['pr_auc'] = float(pr_auc)
            except Exception as e:
                logger.warning(f"Could not calculate AUC metrics: {e}")
        
        logger.info(f"Accuracy: {self.metrics['accuracy']:.4f}")
        logger.info(f"Precision: {self.metrics['precision']:.4f}")
        logger.info(f"Recall: {self.metrics['recall']:.4f}")
        logger.info(f"F1-Score: {self.metrics['f1_score']:.4f}")
        
        return self.metrics
    
    def get_classification_report(
        self,
        y_true: pd.Series,
        y_pred: np.ndarray,
    ) -> str:
        """
        Get detailed classification report.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
        
        Returns:
            Classification report string
        """
        report = classification_report(
            y_true, y_pred,
            target_names=['On-Time', 'Delayed'],
            digits=4
        )
        logger.info(f"Classification Report:\n{report}")
        return report
    
    def get_threshold_analysis(
        self,
        y_true: pd.Series,
        y_pred_proba: np.ndarray,
    ) -> pd.DataFrame:
        """
        Analyze metrics at different probability thresholds.
        
        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities
        
        Returns:
            DataFrame with metrics at different thresholds
        """
        results = []
        
        for threshold in np.arange(0.1, 1.0, 0.1):
            y_pred = (y_pred_proba[:, 1] >= threshold).astype(int)
            
            results.append({
                'threshold': threshold,
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, zero_division=0),
                'recall': recall_score(y_true, y_pred, zero_division=0),
                'f1': f1_score(y_true, y_pred, zero_division=0),
            })
        
        threshold_df = pd.DataFrame(results)
        logger.info(f"Threshold analysis:\n{threshold_df}")
        
        return threshold_df
    
    def compare_models(
        self,
        models_predictions: Dict[str, Tuple[np.ndarray, np.ndarray]],
        y_true: pd.Series,
    ) -> pd.DataFrame:
        """
        Compare multiple model predictions.
        
        Args:
            models_predictions: Dict of {model_name: (y_pred, y_pred_proba)}
            y_true: True labels
        
        Returns:
            DataFrame with comparison metrics
        """
        comparison_results = []
        
        for model_name, (y_pred, y_pred_proba) in models_predictions.items():
            metrics = self.evaluate(y_true, y_pred, y_pred_proba)
            metrics['model'] = model_name
            comparison_results.append(metrics)
        
        comparison_df = pd.DataFrame(comparison_results)
        logger.info(f"Model Comparison:\n{comparison_df}")
        
        return comparison_df
    
    def save_metrics(self, filepath: str) -> None:
        """
        Save metrics to JSON file.
        
        Args:
            filepath: Path to save metrics
        """
        with open(filepath, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        logger.info(f"Metrics saved to {filepath}")
