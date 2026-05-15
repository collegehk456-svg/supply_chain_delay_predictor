"""Data validation module."""

import pandas as pd
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


class DataValidator:
    """Validate data quality and schema."""
    
    def validate(self, df: pd.DataFrame, required_columns: List[str]) -> Tuple[bool, List[str]]:
        """Validate dataframe.
        
        Args:
            df: DataFrame to validate
            required_columns: List of required column names
            
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Check for empty dataframe
        if len(df) == 0:
            errors.append("DataFrame is empty")
        
        # Check for required columns
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        
        # Check for missing values
        missing_values = df.isnull().sum()
        if missing_values.sum() > 0:
            logger.warning(f"Found missing values: {missing_values[missing_values > 0].to_dict()}")
        
        return len(errors) == 0, errors
