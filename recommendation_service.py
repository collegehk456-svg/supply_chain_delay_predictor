"""Generate operational recommendations based on predictions."""

from typing import List, Dict, Optional


class RecommendationService:
    """Generate actionable recommendations to reduce delays."""
    
    def __init__(self):
        """Initialize recommendation service."""
        self.rules = {
            'high_discount': {
                'threshold': 25,
                'recommendation': 'Reduce Discount',
                'description': 'Consider reducing discount to lower logistics volume',
                'impact': 0.15,
                'cost': 'Revenue impact'
            },
            'heavy_weight': {
                'threshold': 3000,
                'recommendation': 'Expedite Shipping',
                'description': 'Use expedited shipping for heavy packages',
                'impact': 0.10,
                'cost': '$15 per shipment'
            },
            'low_engagement': {
                'threshold': 2,
                'recommendation': 'Proactive Contact',
                'description': 'Send automated pre-delivery SMS/email',
                'impact': 0.07,
                'cost': 'Low (automation)'
            },
            'new_customer': {
                'threshold': 1,
                'recommendation': 'Extra Verification',
                'description': 'Verify address and handling requirements',
                'impact': 0.08,
                'cost': 'QA team time'
            }
        }
    
    def generate(self, 
                shipment_data: Dict,
                predicted_probability: float,
                top_factors: List[str]) -> Dict:
        """Generate recommendations based on shipment and prediction.
        
        Args:
            shipment_data: Input shipment features
            predicted_probability: Predicted probability of delay (0-1)
            top_factors: Top SHAP factors
            
        Returns:
            Dictionary with recommendations
        """
        recommendations = []
        total_impact = 0.0
        
        # Rule 1: High discount
        if shipment_data.get('discount_offered', 0) > self.rules['high_discount']['threshold']:
            recommendations.append({
                'action': f"Reduce discount from {shipment_data['discount_offered']}% to {max(0, shipment_data['discount_offered']-8)}%",
                'reason': 'High discounts drive order volume, straining fulfillment',
                'expected_impact': f"Reduce delay risk by {self.rules['high_discount']['impact']*100:.0f}%",
                'cost': self.rules['high_discount']['cost'],
                'priority': 'HIGH'
            })
            total_impact += self.rules['high_discount']['impact']
        
        # Rule 2: Heavy weight
        if shipment_data.get('weight_in_gms', 0) > self.rules['heavy_weight']['threshold']:
            recommendations.append({
                'action': f"Upgrade {shipment_data['weight_in_gms']}g package to priority shipping",
                'reason': 'Heavy items require special handling and have higher delay risk',
                'expected_impact': f"Reduce delay risk by {self.rules['heavy_weight']['impact']*100:.0f}%",
                'cost': self.rules['heavy_weight']['cost'],
                'priority': 'HIGH'
            })
            total_impact += self.rules['heavy_weight']['impact']
        
        # Rule 3: Low customer calls
        if shipment_data.get('customer_care_calls', 0) < self.rules['low_engagement']['threshold']:
            recommendations.append({
                'action': 'Send proactive pre-delivery notification',
                'reason': 'Customers with low engagement benefit from outreach',
                'expected_impact': f"Reduce delay risk by {self.rules['low_engagement']['impact']*100:.0f}%",
                'cost': self.rules['low_engagement']['cost'],
                'priority': 'MEDIUM'
            })
            total_impact += self.rules['low_engagement']['impact']
        
        # Rule 4: New customer
        if shipment_data.get('prior_purchases', 0) < self.rules['new_customer']['threshold']:
            recommendations.append({
                'action': 'Verify delivery address and special requirements',
                'reason': 'New customers have higher error rates in address/requirements',
                'expected_impact': f"Reduce delay risk by {self.rules['new_customer']['impact']*100:.0f}%",
                'cost': self.rules['new_customer']['cost'],
                'priority': 'MEDIUM'
            })
            total_impact += self.rules['new_customer']['impact']
        
        return {
            'recommendations': recommendations,
            'total_potential_improvement': min(total_impact, 0.50),  # Cap at 50%
            'priority_recommendation': recommendations[0] if recommendations else None,
            'estimated_delay_reduction': f"{min(total_impact, 0.50)*100:.0f}%"
        }