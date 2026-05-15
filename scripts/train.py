"""
Main Training Script
Orchestrates the complete ML pipeline from data loading to model evaluation.
"""

import argparse
import logging
import json
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# Add project root to path
import joblib

# Set default encoding for stdout/stderr to UTF-8 to prevent UnicodeEncodeError on some systems
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import ML pipeline components
from ml_pipeline.data.loader import DataLoader
from ml_pipeline.data.preprocessor import DataPreprocessor
from ml_pipeline.features.engineer import FeatureEngineer
from ml_pipeline.models.trainer import ModelTrainer
from ml_pipeline.models.evaluator import ModelEvaluator

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

    # Data Processing
    logger.info("Data Processing: Initializing preprocessor and feature engineer.")
    preprocessor = DataPreprocessor()
    engineer = FeatureEngineer()

    
    # Get feature names
    numerical_cols = config['features']['numerical']
    categorical_cols = config['features']['categorical']
    target_col = "Reached_on_Time_Y_N"
    
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


def train_model(X_train: pd.DataFrame, y_train: pd.Series) -> ModelTrainer:
    """
    Train the ML model.
    
    Args:
        X_train: Training features
        y_train: Training target
    
    Returns:
        Trained ModelTrainer instance
    """
    logger.info("Model Training: Initializing and training XGBoost model.") # Removed emoji
    
    trainer = ModelTrainer(random_state=42)
    history = trainer.train_xgboost(
        X_train, y_train,
        cv_folds=5,
        early_stopping=True,
        early_stopping_rounds=10
    )
    
    logger.info(f"Cross-validation AUC: {history['cv_mean']:.4f}")
    
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

def main(args):
    """Main training function."""
    logger.info("=" * 80)
    logger.info("Starting ML Pipeline")
    logger.info("=" * 80)
    
    config = get_config()
    
    # Load and prepare data
    X_train, X_test, y_train, y_test, preprocessor, engineer, feature_names = load_and_prepare_data(
        args.data_path,
        config
    )
    
    # Train model
    logger.info("Model Training: Starting model training phase.") # Removed emoji
    trainer = train_model(X_train, y_train, X_test, y_test) # Pass X_test, y_test for early stopping
    
    # Save the raw trained model for SHAP explainer (needed for TreeExplainer)
    trainer.save_model(Path(args.output_path).parent / "model.pkl")

    # Evaluate model
    logger.info("Model Evaluation: Starting model evaluation phase.")
    metrics = evaluate_model(trainer, X_test, y_test)
    
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
