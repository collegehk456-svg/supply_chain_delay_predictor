"""Model training module."""

import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import cross_validate, StratifiedKFold
from sklearn.metrics import roc_auc_score
import joblib
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Train and manage ML models."""
    
    def __init__(self, random_state: int = 42):
        """
        Initialize trainer.
        
        Args:
            random_state: Random seed
        """
        self.random_state = random_state
        self.model = None
    
    def train_xgboost(self, X_train: pd.DataFrame, y_train: pd.Series,
                      X_val: Optional[pd.DataFrame] = None, 
                      y_val: Optional[pd.Series] = None,
                      cv_folds: int = 5, early_stopping: bool = True,
                     early_stopping_rounds: int = 10) -> Dict[str, Any]:
        """Train XGBoost model.
        
        Args:
            X_train: Training features
            y_train: Training target
            cv_folds: Number of cross-validation folds
            X_val: Validation features for early stopping (optional)
            y_val: Validation target for early stopping (optional)
            early_stopping: Whether to use early stopping
            early_stopping_rounds: Rounds for early stopping
            
        Returns:
            Dictionary with training history
        """
        logger.info("Training XGBoost model...")
        
        # Initialize model
        # Optimization: Increased estimators, added scale_pos_weight for imbalance,
        # and tuned tree parameters for better generalization.
        # Early stopping is passed to fit, not the constructor, for CV compatibility
        clf = XGBClassifier(
            n_estimators=500,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.9,
            min_child_weight=2,
            scale_pos_weight=1.2,
            random_state=self.random_state,
            eval_metric='logloss',
            n_jobs=-1
        )
        
        # Cross-validation
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
        
        # Added recall and f1 to scoring metrics
        scoring = {'accuracy': 'accuracy', 'roc_auc': 'roc_auc', 'precision': 'precision', 'recall': 'recall', 'f1': 'f1'}
        cv_results = cross_validate(clf, X_train, y_train, cv=cv, 
                                   scoring=scoring, return_train_score=True)
        
        history = {
            'cv_roc_auc_mean': cv_results['test_roc_auc'].mean(),
            'cv_std': cv_results['test_roc_auc'].std(),
            'train_accuracy': cv_results['train_accuracy'].mean(),
            'test_accuracy': cv_results['test_accuracy'].mean(),
        }

        # Train final model on full training set
        self.model = clf
        fit_params = {}
        if early_stopping and X_val is not None and y_val is not None:
            fit_params['eval_set'] = [(X_val, y_val)]
            # Pass early_stopping_rounds to fit method
            self.model.set_params(early_stopping_rounds=early_stopping_rounds)
            fit_params['verbose'] = False

        self.model.fit(X_train, y_train, **fit_params)

        logger.info(f"XGBoost training completed")
        logger.info(f"CV ROC-AUC: {history['cv_roc_auc_mean']:.4f}")
        
        return history
    
    def save_model(self, filepath: str) -> None:
        """Save trained model.
        
        Args:
            filepath: Path to save model
        """
        if self.model is None:
            raise ValueError("No model to save. Train model first.")
        
        joblib.dump(self.model, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """Load trained model.
        
        Args:
            filepath: Path to load model from
        """
        self.model = joblib.load(filepath)
        logger.info(f"Model loaded from {filepath}")
