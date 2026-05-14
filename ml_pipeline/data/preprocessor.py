"""
Data Preprocessor Module
Handles data cleaning, transformation, and preparation.
"""

import pandas as pd
import numpy as np
import logging
from typing import Tuple, Optional, List
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer

logger = logging.getLogger(__name__)


class DataPreprocessor:
    """Preprocess and transform raw data."""
    
    def __init__(self):
        """Initialize preprocessor."""
        self.numerical_features: List[str] = []
        self.categorical_features: List[str] = []
        self.target_column: str = ""
        self.scalers: dict = {}
        self.encoders: dict = {}
        self.imputers: dict = {}
    
    def identify_features(
        self,
        df: pd.DataFrame,
        numerical_cols: List[str],
        categorical_cols: List[str],
        target_col: str,
    ) -> None:
        """
        Identify and store feature types.
        
        Args:
            df: Input DataFrame
            numerical_cols: List of numerical column names
            categorical_cols: List of categorical column names
            target_col: Target column name
        """
        self.numerical_features = numerical_cols
        self.categorical_features = categorical_cols
        self.target_column = target_col
        
        logger.info(f"Numerical features: {len(numerical_cols)}")
        logger.info(f"Categorical features: {len(categorical_cols)}")
    
    def handle_missing_values(
        self,
        df: pd.DataFrame,
        strategy: str = "mean",
        is_fit: bool = True,
    ) -> pd.DataFrame:
        """
        Handle missing values in data.
        
        Args:
            df: Input DataFrame
            strategy: Imputation strategy (mean, median, most_frequent)
            is_fit: Whether to fit the imputer
        
        Returns:
            DataFrame with missing values handled
        """
        df_copy = df.copy()
        
        # Handle numerical features
        if self.numerical_features:
            if is_fit:
                self.imputers['numerical'] = SimpleImputer(strategy=strategy)
                df_copy[self.numerical_features] = self.imputers['numerical'].fit_transform(
                    df_copy[self.numerical_features]
                )
            else:
                df_copy[self.numerical_features] = self.imputers['numerical'].transform(
                    df_copy[self.numerical_features]
                )
            logger.info(f"Imputed numerical features using {strategy}")
        
        # Handle categorical features
        if self.categorical_features:
            if is_fit:
                self.imputers['categorical'] = SimpleImputer(strategy='most_frequent')
                df_copy[self.categorical_features] = self.imputers['categorical'].fit_transform(
                    df_copy[self.categorical_features]
                )
            else:
                df_copy[self.categorical_features] = self.imputers['categorical'].transform(
                    df_copy[self.categorical_features]
                )
            logger.info("Imputed categorical features using most_frequent")
        
        return df_copy
    
    def handle_outliers(
        self,
        df: pd.DataFrame,
        method: str = "iqr",
        threshold: float = 1.5,
    ) -> pd.DataFrame:
        """
        Handle outliers using IQR method.
        
        Args:
            df: Input DataFrame
            method: Method to use (iqr, zscore)
            threshold: Threshold for outlier detection
        
        Returns:
            DataFrame with outliers handled
        """
        df_copy = df.copy()
        
        if method == "iqr":
            for col in self.numerical_features:
                Q1 = df_copy[col].quantile(0.25)
                Q3 = df_copy[col].quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                # Cap outliers instead of removing
                df_copy[col] = df_copy[col].clip(lower_bound, upper_bound)
            
            logger.info(f"Handled outliers using IQR method with threshold {threshold}")
        
        return df_copy
    
    def encode_categorical(
        self,
        df: pd.DataFrame,
        is_fit: bool = True,
        encoding_type: str = "label",
    ) -> pd.DataFrame:
        """
        Encode categorical variables.
        
        Args:
            df: Input DataFrame
            is_fit: Whether to fit the encoders
            encoding_type: Type of encoding (label, onehot)
        
        Returns:
            DataFrame with encoded categories
        """
        df_copy = df.copy()
        
        if encoding_type == "label":
            for col in self.categorical_features:
                if is_fit:
                    self.encoders[col] = LabelEncoder()
                    df_copy[col] = self.encoders[col].fit_transform(df_copy[col].astype(str))
                else:
                    df_copy[col] = self.encoders[col].transform(df_copy[col].astype(str))
            
            logger.info(f"Encoded {len(self.categorical_features)} categorical features")
        
        elif encoding_type == "onehot":
            df_copy = pd.get_dummies(
                df_copy,
                columns=self.categorical_features,
                drop_first=True,
                dtype=int
            )
            logger.info(f"One-hot encoded {len(self.categorical_features)} categorical features")
        
        return df_copy
    
    def scale_features(
        self,
        df: pd.DataFrame,
        is_fit: bool = True,
    ) -> pd.DataFrame:
        """
        Scale numerical features using StandardScaler.
        
        Args:
            df: Input DataFrame
            is_fit: Whether to fit the scaler
        
        Returns:
            DataFrame with scaled features
        """
        df_copy = df.copy()
        
        if self.numerical_features:
            if is_fit:
                self.scalers['standard'] = StandardScaler()
                df_copy[self.numerical_features] = self.scalers['standard'].fit_transform(
                    df_copy[self.numerical_features]
                )
            else:
                df_copy[self.numerical_features] = self.scalers['standard'].transform(
                    df_copy[self.numerical_features]
                )
            
            logger.info(f"Scaled {len(self.numerical_features)} numerical features")
        
        return df_copy
    
    def preprocess(
        self,
        df: pd.DataFrame,
        is_fit: bool = True,
        handle_outliers: bool = True,
        scale: bool = True,
        encode_categorical: bool = True,
    ) -> pd.DataFrame:
        """
        Apply full preprocessing pipeline.
        
        Args:
            df: Input DataFrame
            is_fit: Whether to fit transformers
            handle_outliers: Whether to handle outliers
            scale: Whether to scale features
            encode_categorical: Whether to encode categories
        
        Returns:
            Preprocessed DataFrame
        """
        logger.info("Starting preprocessing pipeline")
        
        # Handle missing values
        df = self.handle_missing_values(df, is_fit=is_fit)
        
        # Handle outliers
        if handle_outliers:
            df = self.handle_outliers(df)
        
        # Encode categorical features
        if encode_categorical:
            df = self.encode_categorical(df, is_fit=is_fit)
        
        # Scale features
        if scale:
            df = self.scale_features(df, is_fit=is_fit)
        
        logger.info("Preprocessing pipeline completed")
        
        return df
