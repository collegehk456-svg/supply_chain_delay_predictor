"""Feature engineering module."""

import pandas as pd
import numpy as np
import logging
from typing import List

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Engineer and create new features."""
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create engineered features.
        
        Args:
            df: Input dataframe
            
        Returns:
            Dataframe with engineered features
        """
        df = df.copy()
        
        # Weight-based features
        if 'Weight_in_gms' in df.columns:
            df['log_weight'] = np.log1p(df['Weight_in_gms'])
            df['weight_category'] = pd.cut(df['Weight_in_gms'], 
                                           bins=[0, 1000, 5000, 10000],
                                           labels=['light', 'medium', 'heavy'])
            df['weight_category'] = pd.Categorical(df['weight_category']).codes
        
        # Cost-based features
        if 'Cost_of_the_Product' in df.columns:
            df['log_cost'] = np.log1p(df['Cost_of_the_Product'])
            df['cost_category'] = pd.cut(df['Cost_of_the_Product'],
                                        bins=[0, 1000, 5000, 10000, 50000],
                                        labels=['low', 'medium', 'high', 'premium'])
            df['cost_category'] = pd.Categorical(df['cost_category']).codes
        
        # Customer rating features
        if 'Customer_rating' in df.columns:
            df['high_rating'] = (df['Customer_rating'] >= 4).astype(int)
            df['low_rating'] = (df['Customer_rating'] <= 2).astype(int)
        
        # Prior purchases features
        if 'Prior_purchases' in df.columns:
            df['high_prior_purchases'] = (df['Prior_purchases'] >= 5).astype(int)
            df['is_repeat_customer'] = (df['Prior_purchases'] > 0).astype(int)
        
        # Discount features
        if 'Discount_offered' in df.columns:
            df['has_discount'] = (df['Discount_offered'] > 0).astype(int)
            df['high_discount'] = (df['Discount_offered'] >= 10).astype(int)
        
        # Interaction features
        if 'Weight_in_gms' in df.columns and 'Cost_of_the_Product' in df.columns:
            df['weight_cost_ratio'] = df['Weight_in_gms'] / (df['Cost_of_the_Product'] + 1)
        
        if 'Customer_care_calls' in df.columns:
            df['has_customer_calls'] = (df['Customer_care_calls'] > 0).astype(int)
        
        logger.info(f"Created {df.shape[1]} total features (including original)")
        
        return df
