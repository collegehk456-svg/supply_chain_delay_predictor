"""Model training module."""

import pandas as pd
import numpy as np
import xgboost as xgb
from pathlib import Path
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import roc_auc_score, accuracy_score
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
            X_val: Validation features for early stopping (optional)
            y_val: Validation target for early stopping (optional)
            cv_folds: Number of cross-validation folds
            early_stopping: Whether to use early stopping
            early_stopping_rounds: Rounds for early stopping
            
        Returns:
            Dictionary with training history
        """
        logger.info("Training XGBoost model...")
        
        clf = XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.9,
            min_child_weight=2,
            scale_pos_weight=1.2,
            random_state=self.random_state,
            eval_metric='logloss',
            use_label_encoder=False,
            n_jobs=-1
        )
        
        history: Dict[str, Any] = {}
        
        if X_val is None or y_val is None:
            logger.info("No validation set provided. Using cross-validation for reliability.")
            cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
            scoring = {'accuracy': 'accuracy', 'roc_auc': 'roc_auc', 'precision': 'precision', 'recall': 'recall', 'f1': 'f1'}
            cv_results = cross_validate(clf, X_train, y_train, cv=cv, scoring=scoring, return_train_score=True)

            history = {
                'cv_roc_auc_mean': float(cv_results['test_roc_auc'].mean()),
                'cv_std': float(cv_results['test_roc_auc'].std()),
                'train_accuracy': float(cv_results['train_accuracy'].mean()),
                'test_accuracy': float(cv_results['test_accuracy'].mean()),
            }
            logger.info(f"Cross-validation ROC-AUC: {history['cv_roc_auc_mean']:.4f} ± {history['cv_std']:.4f}")
            self.model = clf
            self.model.fit(X_train, y_train, verbose=False)
        else:
            logger.info("Validation set provided. Training with early stopping.")
            dtrain = xgb.DMatrix(X_train, label=y_train)
            dval = xgb.DMatrix(X_val, label=y_val)
            params = {
                'objective': 'binary:logistic',
                'eval_metric': 'logloss',
                'scale_pos_weight': 1.2,
                'eta': 0.05,
                'max_depth': 5,
                'subsample': 0.8,
                'colsample_bytree': 0.9,
                'seed': self.random_state,
                'verbosity': 0,
            }
            callbacks = []
            if early_stopping:
                callbacks.append(xgb.callback.EarlyStopping(rounds=early_stopping_rounds, save_best=True))

            booster = xgb.train(
                params,
                dtrain,
                num_boost_round=100,
                evals=[(dtrain, 'train'), (dval, 'validation')],
                callbacks=callbacks,
                verbose_eval=False,
            )
            
            self.model = XGBClassifier(
                n_estimators=booster.best_iteration if getattr(booster, 'best_iteration', None) is not None else 100,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.8,
                colsample_bytree=0.9,
                min_child_weight=2,
                scale_pos_weight=1.2,
                random_state=self.random_state,
                use_label_encoder=False,
                n_jobs=-1,
            )
            self.model._Booster = booster
            encoder = LabelEncoder().fit([0, 1])
            self.model.__dict__['_le'] = encoder
            self.model.__dict__['classes_'] = encoder.classes_
            self.model.__dict__['n_classes_'] = len(encoder.classes_)
            self.model.__dict__['_n_features_in'] = X_train.shape[1]

            val_proba = booster.predict(dval)
            train_proba = booster.predict(dtrain)
            history = {
                'validation_roc_auc': float(roc_auc_score(y_val, val_proba)),
                'train_accuracy': float(accuracy_score(y_train, (train_proba >= 0.5).astype(int))),
                'validation_accuracy': float(accuracy_score(y_val, (val_proba >= 0.5).astype(int))),
                'best_iteration': int(getattr(booster, 'best_iteration', 0) or 0),
            }
            logger.info(f"Validation ROC-AUC: {history['validation_roc_auc']:.4f}")
        
        logger.info("XGBoost training completed")
        return history
    
    def save_model(self, filepath: str) -> None:
        """Save trained model.
        
        Args:
            filepath: Path to save model
        """
        if self.model is None:
            raise ValueError("No model to save. Train model first.")
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """Load trained model.
        
        Args:
            filepath: Path to load model from
        """
        self.model = joblib.load(filepath)
        logger.info(f"Model loaded from {filepath}")
