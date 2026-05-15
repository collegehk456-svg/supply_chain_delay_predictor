"""SHAP-based model explainability."""

import shap
import numpy as np
import pandas as pd
from typing import Dict, List


class SHAPExplainer:
    """SHAP-based model explainability."""
    
    def __init__(self, model, X_background, feature_names: List[str]):
        """Initialize SHAP explainer.
        
        Args:
            model: Trained XGBoost model
            X_background: Background data for SHAP (sample from training)
            feature_names: List of feature names in order
        """
        self.model = model
        self.feature_names = feature_names
        self.explainer = shap.TreeExplainer(model)
        # Use first 100 rows as background
        if hasattr(X_background, 'iloc'):
            self.background = X_background.iloc[:min(100, len(X_background))]
        else:
            self.background = X_background[:min(100, len(X_background))]
    
    def explain_single(self, X_sample: np.ndarray) -> Dict:
        """Explain prediction for single sample.
        
        Args:
            X_sample: Feature vector (numpy array)
            
        Returns:
            Dictionary with SHAP values and contributions
        """
        if len(X_sample.shape) == 1:
            X_sample = X_sample.reshape(1, -1)
        
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(X_sample)
        
        # Handle binary classification (returns array of length 2)
        if isinstance(shap_values, list) and len(shap_values) == 2:
            # Use values for positive class (delay)
            shap_vals = shap_values[1][0]
        else:
            shap_vals = shap_values[0] if len(shap_values.shape) > 1 else shap_values
        
        # Create contributions dataframe
        contributions = pd.DataFrame({
            'feature': self.feature_names,
            'shap_value': shap_vals,
            'feature_value': X_sample[0],
            'abs_contribution': np.abs(shap_vals)
        })
        
        contributions['contribution_pct'] = (
            contributions['abs_contribution'] / 
            contributions['abs_contribution'].sum() * 100
        )
        
        contributions = contributions.sort_values('contribution_pct', ascending=False)
        
        return {
            'shap_values': shap_vals.tolist(),
            'contributions': contributions.to_dict('records'),
            'top_3_factors': contributions.head(3)['feature'].tolist(),
            'top_3_values': contributions.head(3)['shap_value'].tolist(),
            'top_3_importance': contributions.head(3)['contribution_pct'].tolist()
        }
