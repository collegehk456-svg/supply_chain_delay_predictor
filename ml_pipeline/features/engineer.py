"""
Feature Engineering Module
Creates and transforms features for improved model performance.
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Create and engineer features."""
    
    def __init__(self):
        """Initialize feature engineer."""
        self.created_features: List[str] = []
    
    def create_weight_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create weight-based features.
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame with weight features
        """
        df_copy = df.copy()
        
        # Log transformation of weight
        df_copy['Weight_log'] = np.log1p(df_copy['Weight_in_gms'])
        
        # Weight categories
        df_copy['Weight_category'] = pd.cut(
            df_copy['Weight_in_gms'],
            bins=[0, 500, 1500, 5000, float('inf')],
            labels=['Light', 'Medium', 'Heavy', 'VeryHeavy'],
            include_lowest=True
        )
        
        self.created_features.extend(['Weight_log', 'Weight_category'])
        logger.info("Created weight-based features")
        
        return df_copy
    
    def create_cost_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create cost-based features.
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame with cost features
        """
        df_copy = df.copy()
        
        # Log transformation of cost
        df_copy['Cost_log'] = np.log1p(df_copy['Cost_of_the_Product'])
        
        # Price-per-weight ratio
        df_copy['Price_per_weight'] = (
            df_copy['Cost_of_the_Product'] / df_copy['Weight_in_gms']
        )
        
        # Cost categories
        df_copy['Cost_category'] = pd.cut(
            df_copy['Cost_of_the_Product'],
            bins=[0, 2000, 5000, 10000, float('inf')],
            labels=['Cheap', 'Moderate', 'Expensive', 'VeryExpensive'],
            include_lowest=True
        )
        
        self.created_features.extend(['Cost_log', 'Price_per_weight', 'Cost_category'])
        logger.info("Created cost-based features")
        
        return df_copy
    
    def create_customer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create customer-based features.
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame with customer features
        """
        df_copy = df.copy()
        
        # Customer segment based on purchases and rating
        df_copy['Customer_lifetime_value'] = (
            df_copy['Prior_purchases'] * df_copy['Customer_rating']
        )
        
        # Frequent buyer indicator
        df_copy['Is_frequent_buyer'] = (df_copy['Prior_purchases'] >= 3).astype(int)
        
        # Satisfied customer indicator
        df_copy['Is_satisfied_customer'] = (df_copy['Customer_rating'] >= 4.0).astype(int)
        
        # Customer concern level (inverse of satisfaction)
        df_copy['Customer_concern_calls_ratio'] = (
            df_copy['Customer_care_calls'] / (df_copy['Prior_purchases'] + 1)
        )
        
        self.created_features.extend([
            'Customer_lifetime_value',
            'Is_frequent_buyer',
            'Is_satisfied_customer',
            'Customer_concern_calls_ratio'
        ])
        logger.info("Created customer-based features")
        
        return df_copy
    
    def create_discount_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create discount-based features.
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame with discount features
        """
        df_copy = df.copy()
        
        # Discount categories
        df_copy['Discount_category'] = pd.cut(
            df_copy['Discount_offered'],
            bins=[0, 5, 15, 25, 100],
            labels=['No_discount', 'Low', 'Medium', 'High'],
            include_lowest=True
        )
        
        # High discount flag
        df_copy['Is_high_discount'] = (df_copy['Discount_offered'] > 15).astype(int)
        
        # Discount-cost ratio
        df_copy['Discount_cost_ratio'] = (
            df_copy['Discount_offered'] / 100 * df_copy['Cost_of_the_Product']
        )
        
        self.created_features.extend([
            'Discount_category',
            'Is_high_discount',
            'Discount_cost_ratio'
        ])
        logger.info("Created discount-based features")
        
        return df_copy
    
    def create_shipment_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create shipment-based features.
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame with shipment features
        """
        df_copy = df.copy()
        
        # Shipment risk score based on mode and weight
        mode_risk = {
            'Ship': 0.8,
            'Flight': 0.2,
            'Road': 0.5
        }
        df_copy['Mode_risk_score'] = df_copy['Mode_of_Shipment'].map(mode_risk)
        
        # Weight-mode interaction
        df_copy['Weight_mode_risk'] = (
            df_copy['Weight_in_gms'] / 1000 * df_copy['Mode_risk_score']
        )
        
        # Product importance-mode match
        importance_priority = {
            'Low': 0.3,
            'Medium': 0.6,
            'High': 0.9
        }
        df_copy['Importance_priority'] = df_copy['Product_importance'].map(importance_priority)
        
        self.created_features.extend([
            'Mode_risk_score',
            'Weight_mode_risk',
            'Importance_priority'
        ])
        logger.info("Created shipment-based features")
        
        return df_copy
    
    def create_combined_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create combined interaction features.
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame with combined features
        """
        df_copy = df.copy()
        
        # Risk score combining multiple factors
        if 'Mode_risk_score' in df_copy.columns:
            df_copy['Overall_risk_score'] = (
                df_copy['Mode_risk_score'] * 0.3 +
                (df_copy['Weight_in_gms'] / 5000) * 0.3 +
                (1 - df_copy['Customer_rating'] / 5) * 0.2 +
                (df_copy['Discount_offered'] / 100) * 0.2
            )
        
        # Delivery complexity
        df_copy['Delivery_complexity'] = (
            df_copy['Weight_in_gms'] / 1000 +
            df_copy['Cost_of_the_Product'] / 10000 +
            df_copy['Discount_offered'] / 100
        )
        
        self.created_features.extend([
            'Overall_risk_score',
            'Delivery_complexity'
        ])
        logger.info("Created combined features")
        
        return df_copy
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply full feature engineering pipeline.
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame with engineered features
        """
        logger.info("Starting feature engineering pipeline")
        
        df = self.create_weight_features(df)
        df = self.create_cost_features(df)
        df = self.create_customer_features(df)
        df = self.create_discount_features(df)
        df = self.create_shipment_features(df)
        df = self.create_combined_features(df)
        
        logger.info(f"Created {len(self.created_features)} new features")
        logger.info(f"Final shape: {df.shape}")
        
        return df
