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
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import ML pipeline components
from ml_pipeline.data.loader import DataLoader
from ml_pipeline.data.preprocessor import DataPreprocessor
from ml_pipeline.features.engineer import FeatureEngineer
from ml_pipeline.models.trainer import ModelTrainer
from ml_pipeline.models.evaluator import ModelEvaluator

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
    
    # Load data
    loader = DataLoader(data_dir="data/")
    
    # For demo, create sample data if file doesn't exist
    try:
        df = loader.load_raw_data("train.csv")
    except FileNotFoundError:
        logger.warning("Train data not found, creating sample data for demonstration")
        df = create_sample_data()
    
    logger.info(f"Loaded data shape: {df.shape}")
    
    # Get feature names
    numerical_cols = config['features']['numerical']
    categorical_cols = config['features']['categorical']
    target_col = "Reached_on_Time_Y_N"
    
    # Prepare preprocessor
    preprocessor = DataPreprocessor()
    preprocessor.identify_features(df, numerical_cols, categorical_cols, target_col)
    
    # Preprocess data
    logger.info("Preprocessing data...")
    df_processed = preprocessor.preprocess(
        df,
        is_fit=True,
        handle_outliers=True,
        scale=True,
        encode_categorical=True
    )
    
    # Feature engineering
    logger.info("Engineering features...")
    engineer = FeatureEngineer()
    df_processed = engineer.engineer_features(df_processed)
    
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
    
    return X_train, X_test, y_train, y_test, X.columns.tolist()


def train_model(X_train: pd.DataFrame, y_train: pd.Series) -> ModelTrainer:
    """
    Train the ML model.
    
    Args:
        X_train: Training features
        y_train: Training target
    
    Returns:
        Trained ModelTrainer instance
    """
    logger.info("Training model...")
    
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
    logger.info("Evaluating model...")
    
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
    
    return metrics


def save_model(trainer: ModelTrainer, model_path: str) -> None:
    """Save trained model."""
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    trainer.save_model(model_path)
    logger.info(f"Model saved to {model_path}")


def load_config() -> dict:
    """Load configuration."""
    return {
        'data': {
            'test_size': 0.2,
            'random_state': 42,
        },
        'features': {
            'numerical': [
                'Customer_care_calls',
                'Customer_rating',
                'Cost_of_the_Product',
                'Prior_purchases',
                'Discount_offered',
                'Weight_in_gms',
            ],
            'categorical': [
                'Warehouse_block',
                'Mode_of_Shipment',
                'Product_importance',
                'Gender',
            ],
        },
        'model': {
            'type': 'xgboost',
            'threshold': 0.5,
        },
    }


def create_sample_data() -> pd.DataFrame:
    """Create sample data for demonstration."""
    np.random.seed(42)
    n_samples = 1000
    
    df = pd.DataFrame({
        'Warehouse_block': np.random.choice(['A', 'B', 'C', 'D', 'E', 'F'], n_samples),
        'Mode_of_Shipment': np.random.choice(['Ship', 'Flight', 'Road'], n_samples),
        'Customer_care_calls': np.random.randint(0, 7, n_samples),
        'Customer_rating': np.random.uniform(1, 5, n_samples).round(1),
        'Cost_of_the_Product': np.random.randint(100, 50000, n_samples),
        'Prior_purchases': np.random.randint(0, 15, n_samples),
        'Product_importance': np.random.choice(['Low', 'Medium', 'High'], n_samples),
        'Gender': np.random.choice(['M', 'F'], n_samples),
        'Discount_offered': np.random.uniform(0, 100, n_samples).round(1),
        'Weight_in_gms': np.random.randint(100, 10000, n_samples),
        'Reached_on_Time_Y_N': np.random.randint(0, 2, n_samples),
    })
    
    return df


def main(args):
    """Main training function."""
    logger.info("=" * 80)
    logger.info("Starting ML Pipeline")
    logger.info("=" * 80)
    
    # Load configuration
    config = load_config()
    
    # Load and prepare data
    X_train, X_test, y_train, y_test, feature_names = load_and_prepare_data(
        args.data_path,
        config
    )
    
    # Train model
    trainer = train_model(X_train, y_train)
    
    # Evaluate model
    metrics = evaluate_model(trainer, X_test, y_test)
    
    # Save model
    save_model(trainer, args.output_path)
    
    # Save metrics
    metrics_file = Path(args.output_path).parent / "metrics.json"
    with open(metrics_file, 'w') as f:
        # Convert numpy types to native Python types for JSON serialization
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
