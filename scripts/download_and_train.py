"""
Complete script to download dataset from Kaggle and train the model.
Handles data loading, preprocessing, feature engineering, and model training.
"""
import os
import sys
import logging

import argparse
import logging
import json
from pathlib import Path
from datetime import datetime
import sys

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# Try to import kagglehub, install if not available
try:
    import kagglehub
except ImportError:
    print("Installing kagglehub...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "kagglehub"])
    import kagglehub

# Set default encoding for stdout/stderr to UTF-8 to prevent UnicodeEncodeError on some systems
os.environ.setdefault('PYTHONIOENCODING', 'utf-8')

# Import ML pipeline components
from src.ml_pipeline.data.loader import DataLoader
from src.ml_pipeline.data.preprocessor import DataPreprocessor
from src.ml_pipeline.features.engineer import FeatureEngineer
from src.ml_pipeline.models.trainer import ModelTrainer
from src.ml_pipeline.models.evaluator import ModelEvaluator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def download_dataset() -> str:
    """
    Download the E-Commerce Shipping Dataset from Kaggle.
    
    Returns:
        Path to the downloaded dataset
    """
    logger.info("Downloading dataset from Kaggle...")
    logger.info("Dataset: prachi13/customer-analytics")
    
    try:
        path = kagglehub.dataset_download("prachi13/customer-analytics")
        logger.info(f"Dataset downloaded successfully to: {path}")
        return path
    except Exception as e:
        logger.error(f"Failed to download dataset: {e}")
        logger.info("Make sure you have:")
        logger.info("1. Kaggle account set up")
        logger.info("2. API credentials at ~/.kaggle/kaggle.json")
        logger.info("3. kagglehub installed: pip install kagglehub")
        raise


def find_data_file(dataset_path: str) -> str:
    """
    Find the main data CSV file in the downloaded dataset.
    
    Args:
        dataset_path: Path to downloaded dataset
        
    Returns:
        Path to the CSV file
    """
    dataset_dir = Path(dataset_path)
    
    # Look for CSV files
    csv_files = list(dataset_dir.glob("*.csv"))
    
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {dataset_path}")
    
    # Sort by size (largest is likely the main dataset)
    csv_files.sort(key=lambda x: x.stat().st_size, reverse=True)
    
    logger.info(f"Found {len(csv_files)} CSV files")
    for i, f in enumerate(csv_files):
        logger.info(f"  {i+1}. {f.name} ({f.stat().st_size / 1024:.1f} KB)")
    
    selected_file = csv_files[0]
    logger.info(f"Using: {selected_file.name}")
    
    return str(selected_file)


def load_and_prepare_data(data_path: str, config: dict) -> tuple:
    """
    Load and prepare data for training.
    
    Args:
        data_path: Path to data file
        config: Configuration dictionary
    
    Returns:
        Tuple of (X_train, X_test, y_train, y_test, feature_names)
    """
    logger.info("=" * 80)
    logger.info("DATA LOADING AND PREPARATION")
    logger.info("=" * 80)
    
    # Load raw data
    logger.info(f"Loading data from: {data_path}")
    df = pd.read_csv(data_path)
    logger.info(f"Loaded data shape: {df.shape}")
    logger.info(f"Columns: {df.columns.tolist()}")
    
    # Display first few rows
    logger.info(f"\nFirst few rows:\n{df.head()}")
    logger.info(f"\nData types:\n{df.dtypes}")
    logger.info(f"\nMissing values:\n{df.isnull().sum()}")
    
    # Identify target column (handle different naming conventions)
    target_candidates = ['Reached.on.Time_Y/N', 'Reached_on_Time_Y_N', 'target', 'delayed']
    target_col = None
    
    for candidate in target_candidates:
        if candidate in df.columns:
            target_col = candidate
            break
    
    if target_col is None:
        # Try to find a binary column that could be target
        for col in df.columns:
            if df[col].dtype in ['int64', 'int32'] and set(df[col].unique()).issubset({0, 1}):
                target_col = col
                logger.info(f"Using '{col}' as target variable")
                break
    
    if target_col is None:
        raise ValueError(f"Could not identify target column. Available columns: {df.columns.tolist()}")
    
    logger.info(f"\nTarget column: {target_col}")
    logger.info(f"Target distribution:\n{df[target_col].value_counts()}")
    
    # Rename target column for consistency
    df['Reached_on_Time_Y_N'] = df[target_col]
    if target_col != 'Reached_on_Time_Y_N':
        df = df.drop(columns=[target_col])
    
    # Normalize column names
    df.columns = [col.replace('.', '_').replace('/', '_') for col in df.columns]

    # Drop metadata columns that are not model features
    non_feature_columns = [col for col in ['ID', 'Id', 'id', 'Shipment_ID', 'shipment_id'] if col in df.columns]
    if non_feature_columns:
        logger.info(f"Dropping non-feature columns: {non_feature_columns}")
        df = df.drop(columns=non_feature_columns)

    # Identify numerical and categorical columns
    numerical_cols = config['features']['numerical']
    categorical_cols = config['features']['categorical']
    
    # Filter to only available columns
    numerical_cols = [col for col in numerical_cols if col in df.columns]
    categorical_cols = [col for col in categorical_cols if col in df.columns]
    
    logger.info(f"\nNumerical features: {numerical_cols}")
    logger.info(f"Categorical features: {categorical_cols}")
    
    # Prepare preprocessor
    preprocessor = DataPreprocessor()
    preprocessor.identify_features(df, numerical_cols, categorical_cols, 'Reached_on_Time_Y_N')
    
    # Preprocess data
    logger.info("\nPreprocessing data...")
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
    
    logger.info(f"Features after engineering: {df_processed.shape[1]}")
    
    # Prepare features and target
    X = df_processed.drop(columns=['Reached_on_Time_Y_N'])
    y = df_processed['Reached_on_Time_Y_N']
    
    # Train-test split
    logger.info("\nTrain-test split...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=config['data'].get('test_size', 0.2),
        random_state=config['data'].get('random_state', 42),
        stratify=y
    )
    
    logger.info(f"Training set shape: {X_train.shape}")
    logger.info(f"Test set shape: {X_test.shape}")
    logger.info(f"Class distribution (train): {y_train.value_counts().to_dict()}")
    logger.info(f"Class distribution (test): {y_test.value_counts().to_dict()}")
    
    return X_train, X_test, y_train, y_test, X.columns.tolist()


def train_model(X_train: pd.DataFrame, y_train: pd.Series,
                X_val: pd.DataFrame, y_val: pd.Series) -> ModelTrainer:
    """
    Train the ML model.
    
    Args:
        X_train: Training features
        y_train: Training target
        X_val: Validation features
        y_val: Validation target
    
    Returns:
        Trained ModelTrainer instance
    """
    logger.info("\n" + "=" * 80)
    logger.info("MODEL TRAINING")
    logger.info("=" * 80)
    
    trainer = ModelTrainer(random_state=42)
    history = trainer.train_xgboost(
        X_train,
        y_train,
        X_val=X_val,
        y_val=y_val,
        cv_folds=5,
        early_stopping=True,
        early_stopping_rounds=10
    )
    
    if 'validation_roc_auc' in history:
        logger.info(f"Validation ROC-AUC: {history['validation_roc_auc']:.4f}")
    elif 'cv_roc_auc_mean' in history:
        logger.info(f"Cross-validation ROC-AUC: {history['cv_roc_auc_mean']:.4f}")
    
    if 'validation_accuracy' in history:
        logger.info(f"Validation Accuracy: {history['validation_accuracy']:.4f}")
    if 'train_accuracy' in history:
        logger.info(f"Train Accuracy: {history['train_accuracy']:.4f}")
    
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
    logger.info("\n" + "=" * 80)
    logger.info("MODEL EVALUATION")
    logger.info("=" * 80)
    
    # Predictions
    y_pred = trainer.model.predict(X_test)
    y_pred_proba = trainer.model.predict_proba(X_test)
    
    # Evaluation
    evaluator = ModelEvaluator()
    metrics = evaluator.evaluate(y_test, y_pred, y_pred_proba)
    
    # Print results
    logger.info("\n📊 EVALUATION METRICS:")
    logger.info(f"  Accuracy:  {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    logger.info(f"  Precision: {metrics['precision']:.4f}")
    logger.info(f"  Recall:    {metrics['recall']:.4f}")
    logger.info(f"  F1-Score:  {metrics['f1_score']:.4f}")
    logger.info(f"  ROC-AUC:   {metrics.get('roc_auc', 'N/A'):.4f}")
    
    # Classification report
    report = evaluator.get_classification_report(y_test, y_pred)
    logger.info(f"\n📋 CLASSIFICATION REPORT:\n{report}")
    
    # Feature importance
    logger.info("\nTOP 10 FEATURE IMPORTANCE:")
    importance_df = evaluator.get_feature_importance(trainer.model)
    if not importance_df.empty:
        for idx, row in importance_df.head(10).iterrows():
            logger.info(f"  {row['feature']:.<40} {row['importance']:>8.4f}")
    
    return metrics


def save_model(trainer: ModelTrainer, model_path: str) -> None:
    """Save trained model."""
    Path(model_path).parent.mkdir(parents=True, exist_ok=True)
    trainer.save_model(model_path)
    logger.info(f"✅ Model saved to {model_path}")


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


def main(args):
    """Main training function."""
    logger.info("\n")
    logger.info("=" * 40)
    logger.info("SMARTSHIP AI - MODEL TRAINING PIPELINE")
    logger.info("=" * 40)
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Create logs directory (if not exists)
        Path('logs').mkdir(exist_ok=True)
        
        # Load configuration
        config = load_config()
        
        # Download dataset from Kaggle
        if args.download:
            dataset_path = download_dataset()
            data_file = find_data_file(dataset_path)
        else:
            data_file = args.data_path
        
        # Load and prepare data
        X_train, X_test, y_train, y_test, preprocessor, engineer, feature_names = load_and_prepare_data(
            data_file,
            config
        )
        
        # Train model
        trainer = train_model(X_train, y_train)
        
        # Save the raw trained model for SHAP explainer
        trainer.save_model(Path(args.output_path).parent / "model.pkl")

        # Evaluate model
        metrics = evaluate_model(trainer, X_test, y_test)
        
        # Save the complete prediction pipeline
        from ml_pipeline.models.predictor import ModelPredictor # Import here to avoid circular dependency
        full_predictor_pipeline = ModelPredictor(
            preprocessor=preprocessor,
            engineer=engineer,
            model=trainer.model
        )
        full_predictor_pipeline.save(Path(args.output_path).parent / "full_pipeline.pkl")

        # Save preprocessor components (scaler and encoders) separately for SHAP explainer
        # And save X_train_processed for SHAP background
        joblib.dump(preprocessor.scaler, Path(args.output_path).parent / "scaler.pkl")
        joblib.dump(preprocessor.label_encoders, Path(args.output_path).parent / "label_encoders.pkl")
        X_train.to_csv(Path(args.output_path).parent / "X_train_processed.csv", index=False)
        logger.info("Preprocessor components and processed training data saved for SHAP.")
        
        # Save metrics
        metrics_file = Path(args.output_path).parent / "metrics.json"
        with open(metrics_file, 'w') as f:
            metrics_json = {
                k: float(v) if isinstance(v, (np.floating, float)) else str(v)
                for k, v in metrics.items() if k != 'confusion_matrix'
            }
            json.dump(metrics_json, f, indent=2)
        logger.info(f"📊 Metrics saved to {metrics_file}")
        
        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("TRAINING COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info(f"\n📈 Model Performance Summary:")
        logger.info(f"  • Accuracy:  {metrics['accuracy']*100:.2f}%")
        logger.info(f"  • Precision: {metrics['precision']:.4f}")
        logger.info(f"  • Recall:    {metrics['recall']:.4f}")
        logger.info(f"  • F1-Score:  {metrics['f1_score']:.4f}")
        logger.info(f"  • ROC-AUC:   {metrics['roc_auc']:.4f}")
        logger.info(f"\n📁 Output Files:")
        logger.info(f"  • Model: {args.output_path}")
        logger.info(f"  • Metrics: {metrics_file}")
        logger.info(f"  • Logs: logs/training.log")
        logger.info("\n🎉 Ready for deployment!")
        logger.info("=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"\nTraining failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download Kaggle dataset and train Supply Chain Delay Prediction Model",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download from Kaggle and train
  python scripts/download_and_train.py --download
  
  # Train with local data
  python scripts/download_and_train.py --data-path data/raw/train.csv
        """
    )
    
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download dataset from Kaggle (requires kagglehub and API credentials)"
    )
    parser.add_argument(
        "--data-path",
        type=str,
        default="data/raw/train.csv",
        help="Path to training data (used if --download is not specified)"
    )
    parser.add_argument(
        "--output-path",
        type=str,
        default="models/production/model.pkl",
        help="Path to save trained model"
    )
    
    args = parser.parse_args()
    main(args)
