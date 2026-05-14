"""
Data Loader Module
Handles loading and caching of datasets.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Tuple, Optional
import pickle

logger = logging.getLogger(__name__)


class DataLoader:
    """Load and manage datasets."""
    
    def __init__(self, data_dir: str = "data/"):
        """
        Initialize DataLoader.
        
        Args:
            data_dir: Base directory for data files
        """
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
    
    def load_raw_data(self, filename: str) -> pd.DataFrame:
        """
        Load raw data from CSV.
        
        Args:
            filename: Name of CSV file in raw directory
        
        Returns:
            Loaded DataFrame
        """
        filepath = self.raw_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        logger.info(f"Loading raw data from {filepath}")
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns")
        
        return df
    
    def save_processed_data(self, df: pd.DataFrame, filename: str) -> None:
        """
        Save processed data to CSV.
        
        Args:
            df: DataFrame to save
            filename: Name for output file
        """
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        filepath = self.processed_dir / filename
        
        df.to_csv(filepath, index=False)
        logger.info(f"Saved processed data to {filepath}")
    
    def load_processed_data(self, filename: str) -> pd.DataFrame:
        """
        Load processed data from CSV.
        
        Args:
            filename: Name of CSV file in processed directory
        
        Returns:
            Loaded DataFrame
        """
        filepath = self.processed_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Processed data file not found: {filepath}")
        
        logger.info(f"Loading processed data from {filepath}")
        df = pd.read_csv(filepath)
        
        return df
    
    def save_pickle(self, obj: object, filename: str, subdir: str = "processed") -> None:
        """
        Save object to pickle file.
        
        Args:
            obj: Object to pickle
            filename: Name for output file
            subdir: Subdirectory (processed, features, etc.)
        """
        save_dir = self.data_dir / subdir
        save_dir.mkdir(parents=True, exist_ok=True)
        filepath = save_dir / filename
        
        with open(filepath, 'wb') as f:
            pickle.dump(obj, f)
        logger.info(f"Saved pickle to {filepath}")
    
    def load_pickle(self, filename: str, subdir: str = "processed") -> object:
        """
        Load object from pickle file.
        
        Args:
            filename: Name of pickle file
            subdir: Subdirectory (processed, features, etc.)
        
        Returns:
            Unpickled object
        """
        filepath = self.data_dir / subdir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Pickle file not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            obj = pickle.load(f)
        logger.info(f"Loaded pickle from {filepath}")
        
        return obj
    
    def get_data_info(self, df: pd.DataFrame) -> dict:
        """
        Get basic information about dataset.
        
        Args:
            df: Input DataFrame
        
        Returns:
            Dictionary with data info
        """
        return {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 ** 2,
        }
