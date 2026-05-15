"""
Main Training Script
Orchestrates the complete ML pipeline from data loading to model evaluation.
"""

import argparse
import logging
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

import joblib

# Ensure root directory and src package are on sys.path
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# Import ML pipeline components
from src.ml_pipeline.data.preprocessor import DataPreprocessor
from src.ml_pipeline.features.engineer import FeatureEngineer
from src.ml_pipeline.models.trainer import ModelTrainer
from src.ml_pipeline.models.evaluator import ModelEvaluator
from src.ml_pipeline.models.predictor import ModelPredictor

from backend.config import get_config
# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_and_prepare_data(data_path: str, config: dict) -> tuple:
    """
    Load and prepare data for training.
    
    Args:
        data_path: Path to data file
        config: Configuration dictionary
    
    Returns:
        Tuple of (X_train, X_test, y_train, y_test, feature_names)
    """
    logger.info("Loading data...")
    
    # Data Ingestion
    logger.info(f"Data Ingestion: Loading raw data from {data_path}")
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        logger.error(f"Data file not found at {data_path}. Please ensure it exists.")
        raise
    
    logger.info(f"Loaded data shape: {df.shape}")

    # Normalize column names (replace dots with underscores for consistency)
    df.columns = [col.replace('.', '_').replace('/', '_') for col in df.columns]

    # Drop metadata columns that are not model features
    non_feature_columns = [col for col in ['ID', 'Id', 'id', 'Shipment_ID', 'shipment_id'] if col in df.columns]
    if non_feature_columns:
        logger.info(f"Dropping non-feature columns: {non_feature_columns}")
        df = df.drop(columns=non_feature_columns)

    # Data Processing
    logger.info("Data Processing: Initializing preprocessor and feature engineer.")
    preprocessor = DataPreprocessor()
    engineer = FeatureEngineer()

    
    # Detect target column robustly
    target_col = config['features'].get('target', 'Reached_on_Time_Y_N')
    if target_col not in df.columns:
        candidate_columns = [
            'Reached_on_Time_Y_N',
            'Reached_on_Time_Y_N',
            'Reached_on_Time_Y_N'
        ]
        candidate_columns += [col for col in df.columns if 'reached' in col.lower() or 'delay' in col.lower()]
        boolean_columns = [
            col for col in df.columns
            if df[col].dtype in ['int64', 'int32'] and set(df[col].dropna().unique()).issubset({0, 1})
        ]
        candidate_columns.extend(boolean_columns)
        target_col = next((col for col in candidate_columns if col in df.columns), None)

    if target_col is None:
        raise ValueError(f"Could not identify target column. Available columns: {df.columns.tolist()}")

    df = df.rename(columns={target_col: 'Reached_on_Time_Y_N'})
    target_col = 'Reached_on_Time_Y_N'

    numerical_cols = [col for col in config['features']['numerical'] if col in df.columns]
    categorical_cols = [col for col in config['features']['categorical'] if col in df.columns]
    
    # Prepare preprocessor
    preprocessor.identify_features(df, numerical_cols, categorical_cols, target_col)
    
    logger.info("Data Processing: Applying preprocessing steps (scaling, encoding).")
    logger.info("Preprocessing data...")
    df_processed = preprocessor.preprocess(
        df,
        is_fit=True,
        handle_outliers=True,
        scale=True,
        encode_categorical=True
    )
    
    # Feature engineering
    logger.info("Feature Engineering: Creating new features.")
    df_processed = engineer.engineer_features(df_processed)
    
    # Feature Selection (implicit via model training and importance)
    # Prepare features and target
    X = df_processed.drop(columns=[target_col])
    y = df_processed[target_col]
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=config['data'].get('test_size', 0.2),
        random_state=config['data'].get('random_state', 42),
        stratify=y
    )
    
    logger.info(f"Training set shape: {X_train.shape}")
    logger.info(f"Test set shape: {X_test.shape}")
    logger.info(f"Class distribution (train): {y_train.value_counts().to_dict()}")
    
    return X_train, X_test, y_train, y_test, preprocessor, engineer, X.columns.tolist()


def train_model(X_train: pd.DataFrame, y_train: pd.Series,
                X_val: Optional[pd.DataFrame] = None,
                y_val: Optional[pd.Series] = None,
                config: Optional[dict] = None) -> ModelTrainer:
    """
    Train the ML model.
    
    Args:
        X_train: Training features
        y_train: Training target
        X_val: Validation features
        y_val: Validation target
        config: Configuration dictionary
    
    Returns:
        Trained ModelTrainer instance
    """
    logger.info("Model Training: Initializing and training XGBoost model.")
    
    config = config or {}
    trainer = ModelTrainer(random_state=config.get('training', {}).get('random_state', 42))
    history = trainer.train_xgboost(
        X_train,
        y_train,
        X_val=X_val,
        y_val=y_val,
        cv_folds=config.get('training', {}).get('cv_folds', 5),
        early_stopping=config.get('training', {}).get('early_stopping', True),
        early_stopping_rounds=config.get('training', {}).get('early_stopping_rounds', 10)
    )
    
    if 'validation_roc_auc' in history:
        logger.info(f"Validation ROC-AUC: {history['validation_roc_auc']:.4f}")
    elif 'cv_roc_auc_mean' in history:
        logger.info(f"Cross-validation ROC-AUC: {history['cv_roc_auc_mean']:.4f}")
    
    return trainer


def evaluate_model(trainer: ModelTrainer, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    """
    Evaluate the trained model.
    
    Args:
        trainer: Trained ModelTrainer
        X_test: Test features
        y_test: Test target
    
    Returns:
        Dictionary of evaluation metrics
    """
    logger.info("Model Evaluation: Making predictions and calculating metrics.") # Removed emoji
    
    # Predictions
    y_pred = trainer.model.predict(X_test)
    y_pred_proba = trainer.model.predict_proba(X_test)
    
    # Evaluation
    evaluator = ModelEvaluator()
    metrics = evaluator.evaluate(y_test, y_pred, y_pred_proba)
    
    # Print results
    logger.info("\nEvaluation Metrics:")
    logger.info(f"Accuracy:  {metrics['accuracy']:.4f}")
    logger.info(f"Precision: {metrics['precision']:.4f}")
    logger.info(f"Recall:    {metrics['recall']:.4f}")
    logger.info(f"F1-Score:  {metrics['f1_score']:.4f}")
    logger.info(f"ROC-AUC:   {metrics.get('roc_auc', 'N/A')}")
    
    # Classification report
    report = evaluator.get_classification_report(y_test, y_pred)
    logger.info(f"\nClassification Report:\n{report}")

    # Feature importance
    logger.info("\nFeature Selection/Importance: Top 10 features from the model.")
    importance_df = evaluator.get_feature_importance(trainer.model)
    if not importance_df.empty:
        logger.info("\n🎯 TOP 10 FEATURE IMPORTANCE:")
        for idx, row in importance_df.head(10).iterrows():
            logger.info(f"  {row['feature']:.<40} {row['importance']:>8.4f}")
    
    return metrics


def save_model(trainer: ModelTrainer, model_path: str) -> None:
    """Save trained model."""
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    trainer.save_model(model_path)
    logger.info(f"Model saved to {model_path}")
 # Removed save_model function as it's now handled by ModelPredictor.save

def _log_to_mlflow(config: dict, metrics: dict, model_path: Path) -> None:
    """Log experiment to MLflow when tracking server is available."""
    try:
        import mlflow
        import mlflow.sklearn

        uri = config.get("mlflow", {}).get("tracking_uri", "http://localhost:5000")
        mlflow.set_tracking_uri(uri)
        mlflow.set_experiment(
            config.get("mlflow", {}).get("experiment_name", "supply_chain_experiments")
        )
        with mlflow.start_run(run_name=f"xgboost_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            mlflow.log_params({
                "model_type": "xgboost",
                "test_size": config.get("data", {}).get("test_size", 0.2),
            })
            for key, val in metrics.items():
                if isinstance(val, (int, float)) and key != "confusion_matrix":
                    mlflow.log_metric(key, float(val))
            if model_path.exists():
                mlflow.log_artifact(str(model_path))
            mlflow.set_tag("project", "supply_chain")
        logger.info("MLflow run logged successfully")
    except Exception as exc:
        logger.info("MLflow logging skipped (server may be offline): %s", exc)


def main(args):
    """Main training function."""
    logger.info("=" * 80)
    logger.info("STARTING TRAINING")
    logger.info("=" * 80)
    
    config = get_config()
    
    # Load and prepare data
    logger.info("LOADING DATA")
    X_train, X_test, y_train, y_test, preprocessor, engineer, feature_names = load_and_prepare_data(
        args.data_path,
        config
    )
    
    # Train model
    logger.info("TRAINING MODEL")
    trainer = train_model(X_train, y_train, X_test, y_test, config=config)
    
    # Save the raw trained model for SHAP explainer (needed for TreeExplainer)
    trainer.save_model(Path(args.output_path).parent / "model.pkl")

    # Evaluate model
    metrics = evaluate_model(trainer, X_test, y_test)
    logger.info("EVALUATION COMPLETE")
    
    # Save the complete prediction pipeline
    logger.info("Saving complete MLOps prediction pipeline.")
    full_predictor_pipeline = ModelPredictor(
        preprocessor=preprocessor,
        engineer=engineer,
        model=trainer.model
    )
    full_predictor_pipeline.save(Path(args.output_path).parent / "full_pipeline.pkl")

    # Save preprocessor components (scaler and encoders) separately for SHAP explainer
    # This is a temporary measure until SHAP can work directly with the full pipeline
    joblib.dump(preprocessor.scaler, Path(args.output_path).parent / "scaler.pkl")
    joblib.dump(preprocessor.label_encoders, Path(args.output_path).parent / "label_encoders.pkl")
    # Also save X_train_processed for SHAP background
    X_train.to_csv(Path(args.output_path).parent / "X_train_processed.csv", index=False) # X_train is already processed
    logger.info("Preprocessor components and processed training data saved for SHAP.")
    # Save metrics
    metrics_file = Path(args.output_path).parent / "metrics.json" # Removed emoji
    with open(metrics_file, 'w') as f:
        metrics_json = {k: float(v) if isinstance(v, (np.floating, float)) else v 
                       for k, v in metrics.items() if k != 'confusion_matrix'}
        json.dump(metrics_json, f, indent=2)
    logger.info(f"Metrics saved to {metrics_file}")

    _log_to_mlflow(config, metrics, Path(args.output_path).parent / "full_pipeline.pkl")
    
    logger.info("=" * 80)
    logger.info("Pipeline completed successfully!")
    logger.info("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Supply Chain Delay Prediction Model")
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/raw/train.csv",
        help="Path to training data"
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="models/production/model.pkl",
        help="Path to save trained model"
    )
    
    args = parser.parse_args()
    main(args)
