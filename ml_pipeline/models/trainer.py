"""
Model Training Module
Handles model training with hyperparameter tuning.
"""

import pandas as pd
import numpy as np
import logging
from typing import Tuple, Dict, Any, Optional
import xgboost as xgb
from sklearn.model_selection import cross_val_score, GridSearchCV, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import joblib
from pathlib import Path

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Train and optimize ML models."""
    
    def __init__(self, random_state: int = 42):
        """
        Initialize ModelTrainer.
        
        Args:
            random_state: Random seed for reproducibility
        """
        self.random_state = random_state
        self.model: Optional[Any] = None
        self.training_history: Dict[str, Any] = {}
    
    def train_xgboost(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        cv_folds: int = 5,
        early_stopping: bool = True,
        early_stopping_rounds: int = 10,
    ) -> Dict[str, Any]:
        """
        Train XGBoost model.
        
        Args:
            X_train: Training features
            y_train: Training target
            cv_folds: Number of cross-validation folds
            early_stopping: Whether to use early stopping
            early_stopping_rounds: Rounds for early stopping
        
        Returns:
            Dictionary with training results
        """
        logger.info("Training XGBoost model")
        
        # XGBoost parameters
        params = {
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
            'max_depth': 6,
            'learning_rate': 0.1,
            'min_child_weight': 1,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'lambda': 1.0,
            'alpha': 0.0,
            'random_state': self.random_state,
            'n_jobs': -1,
            'tree_method': 'hist',
        }
        
        # Initialize model
        self.model = xgb.XGBClassifier(**params)
        
        # Train model
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_train, y_train)] if early_stopping else None,
            early_stopping_rounds=early_stopping_rounds if early_stopping else None,
            verbose=False
        )
        
        # Cross-validation
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=cv, scoring='roc_auc')
        
        self.training_history = {
            'cv_scores': cv_scores.tolist(),
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std()),
            'training_samples': len(X_train),
            'feature_importance': dict(zip(X_train.columns, self.model.feature_importances_)),
        }
        
        logger.info(f"Cross-validation AUC: {self.training_history['cv_mean']:.4f} "
                   f"(+/- {self.training_history['cv_std']:.4f})")
        
        return self.training_history
    
    def hyperparameter_tuning(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        param_grid: Optional[Dict[str, list]] = None,
        cv_folds: int = 5,
    ) -> Dict[str, Any]:
        """
        Perform hyperparameter tuning using GridSearchCV.
        
        Args:
            X_train: Training features
            y_train: Training target
            param_grid: Parameter grid for tuning
            cv_folds: Number of cross-validation folds
        
        Returns:
            Dictionary with tuning results
        """
        logger.info("Starting hyperparameter tuning")
        
        if param_grid is None:
            param_grid = {
                'max_depth': [4, 6, 8],
                'learning_rate': [0.01, 0.1, 0.3],
                'n_estimators': [100, 200],
                'subsample': [0.8, 1.0],
            }
        
        base_model = xgb.XGBClassifier(
            objective='binary:logistic',
            eval_metric='auc',
            random_state=self.random_state,
            n_jobs=-1,
        )
        
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=cv_folds,
            scoring='roc_auc',
            n_jobs=-1,
            verbose=1,
        )
        
        grid_search.fit(X_train, y_train)
        
        self.model = grid_search.best_estimator_
        
        results = {
            'best_params': grid_search.best_params_,
            'best_score': float(grid_search.best_score_),
            'cv_results': grid_search.cv_results_,
        }
        
        logger.info(f"Best parameters: {results['best_params']}")
        logger.info(f"Best AUC: {results['best_score']:.4f}")
        
        return results
    
    def save_model(self, filepath: str) -> None:
        """
        Save trained model to file.
        
        Args:
            filepath: Path to save model
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """
        Load trained model from file.
        
        Args:
            filepath: Path to model file
        """
        self.model = joblib.load(filepath)
        logger.info(f"Model loaded from {filepath}")
    
    def get_feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """
        Get feature importance from trained model.
        
        Args:
            top_n: Number of top features to return
        
        Returns:
            DataFrame with feature importance scores
        """
        if self.model is None:
            raise ValueError("No model trained yet")
        
        importance_dict = dict(zip(
            getattr(self.model, 'feature_names_in_', None) or range(len(self.model.feature_importances_)),
            self.model.feature_importances_
        ))
        
        importance_df = pd.DataFrame([
            {'feature': k, 'importance': v}
            for k, v in importance_dict.items()
        ]).sort_values('importance', ascending=False)
        
        return importance_df.head(top_n)
