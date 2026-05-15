"""Data loading module."""

import pandas as pd
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Load and manage data from various sources."""
    
    def __init__(self, data_dir: str = "data/"):
        """Initialize data loader.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_raw_data(self, filename: str) -> pd.DataFrame:
        """Load raw data from CSV file.
        
        Args:
            filename: Name of the CSV file
            
        Returns:
            DataFrame with loaded data
        """
        filepath = self.data_dir / "raw" / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        logger.info(f"Loading data from {filepath}")
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")
        
        return df
    
    def save_processed_data(self, df: pd.DataFrame, filename: str) -> None:
        """Save processed data to CSV file.
        
        Args:
            df: DataFrame to save
            filename: Name of the CSV file
        """
        output_dir = self.data_dir / "processed"
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / filename
        
        df.to_csv(filepath, index=False)
        logger.info(f"Saved processed data to {filepath}")
    
    def save_features(self, df: pd.DataFrame, filename: str) -> None:
        """Save engineered features to CSV file.
        
        Args:
            df: DataFrame with features
            filename: Name of the CSV file
        """
        output_dir = self.data_dir / "features"
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / filename
        
        df.to_csv(filepath, index=False)
        logger.info(f"Saved features to {filepath}")
