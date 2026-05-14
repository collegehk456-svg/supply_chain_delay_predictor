"""Data preprocessing module."""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Preprocess and clean data."""
    
    def __init__(self):
        """Initialize preprocessor."""
        self.numerical_cols: List[str] = []
        self.categorical_cols: List[str] = []
        self.target_col: Optional[str] = None
        self.scaler: Optional[StandardScaler] = None
        self.label_encoders: dict = {}
    
    def identify_features(self, df: pd.DataFrame, numerical: List[str], 
                         categorical: List[str], target: str) -> None:
        """Identify and store feature information.
        
        Args:
            df: Input dataframe
            numerical: List of numerical column names
            categorical: List of categorical column names
            target: Target column name
        """
        self.numerical_cols = numerical
        self.categorical_cols = categorical
        self.target_col = target
        logger.info(f"Identified {len(numerical)} numerical and {len(categorical)} categorical features")
    
    def preprocess(self, df: pd.DataFrame, is_fit: bool = True, 
                   handle_outliers: bool = True, scale: bool = True,
                   encode_categorical: bool = True) -> pd.DataFrame:
        """Preprocess data with multiple steps.
        
        Args:
            df: Input dataframe
            is_fit: Whether to fit transformers on this data
            handle_outliers: Whether to handle outliers
            scale: Whether to scale numerical features
            encode_categorical: Whether to encode categorical features
            
        Returns:
            Preprocessed dataframe
        """
        df_processed = df.copy()
        
        # Handle missing values
        logger.info("Handling missing values...")
        df_processed = self._handle_missing_values(df_processed)
        
        # Handle outliers
        if handle_outliers:
            logger.info("Handling outliers...")
            df_processed = self._handle_outliers(df_processed)
        
        # Scale numerical features
        if scale:
            logger.info("Scaling numerical features...")
            df_processed = self._scale_features(df_processed, is_fit)
        
        # Encode categorical features
        if encode_categorical:
            logger.info("Encoding categorical features...")
            df_processed = self._encode_categorical(df_processed, is_fit)
        
        return df_processed
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values."""
        df = df.copy()
        
        # Numerical: fill with median
        for col in self.numerical_cols:
            if col in df.columns and df[col].isnull().any():
                median = df[col].median()
                df[col].fillna(median, inplace=True)
        
        # Categorical: fill with mode
        for col in self.categorical_cols:
            if col in df.columns and df[col].isnull().any():
                mode = df[col].mode()[0] if not df[col].mode().empty else 'Unknown'
                df[col].fillna(mode, inplace=True)
        
        return df
    
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle outliers using IQR method."""
        df = df.copy()
        
        for col in self.numerical_cols:
            if col in df.columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Clip outliers
                df[col] = df[col].clip(lower_bound, upper_bound)
        
        return df
    
    def _scale_features(self, df: pd.DataFrame, is_fit: bool) -> pd.DataFrame:
        """Scale numerical features."""
        df = df.copy()
        
        if is_fit:
            self.scaler = StandardScaler()
            scaled_data = self.scaler.fit_transform(df[self.numerical_cols])
        else:
            if self.scaler is None:
                raise ValueError("Scaler not fitted. Set is_fit=True first.")
            scaled_data = self.scaler.transform(df[self.numerical_cols])
        
        df[self.numerical_cols] = scaled_data
        return df
    
    def _encode_categorical(self, df: pd.DataFrame, is_fit: bool) -> pd.DataFrame:
        """Encode categorical features."""
        df = df.copy()
        
        for col in self.categorical_cols:
            if col in df.columns:
                if is_fit:
                    encoder = LabelEncoder()
                    df[col] = encoder.fit_transform(df[col].astype(str))
                    self.label_encoders[col] = encoder
                else:
                    if col not in self.label_encoders:
                        raise ValueError(f"Encoder for {col} not fitted.")
                    df[col] = self.label_encoders[col].transform(df[col].astype(str))
        
        return df
