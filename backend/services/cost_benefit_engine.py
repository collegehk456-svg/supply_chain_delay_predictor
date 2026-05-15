"""
Cost-Benefit & Intervention Optimization Engine
Converts predictions into actionable, ROI-justified operational decisions.
Core differentiator: Managers see YES/NO + cost, not probability scores.
"""

from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


# Industry-calibrated intervention costs (per shipment)
INTERVENTION_COSTS = {
    "expedite_to_flight": 25.0,        # Upgrade from Ship to Flight
    "manual_priority_sort": 8.0,        # Priority handling in warehouse
    "customer_proactive_notification": 3.0,  # SMS/Email alert
    "reroute_to_closer_warehouse": 12.0,    # Rerouting + repack
}

# Loss prevention rates (% of expected loss avoided by each action)
MITIGATION_RATES = {
    "expedite_to_flight": 0.65,         # 65% delay reduction
    "manual_priority_sort": 0.42,       # 42% delay reduction
    "customer_proactive_notification": 0.15,  # Manages expectations, less actual prevention
    "reroute_to_closer_warehouse": 0.48,     # 48% delay reduction
}

# Base penalty assumption
AVG_DELAY_PENALTY_USD = 85.0  # $85 per late delivery (handling + recovery)
HIGH_VALUE_MULTIPLIER = 1.35  # Premium items have 35% higher penalty


def calculate_expected_loss(
    probability_delayed: float,
    cost_of_product: float,
    mode_of_shipment: str,
    prediction: int = 1,
) -> float:
    """
    Calculate expected loss if this shipment delays (USD).
    
    Args:
        probability_delayed: Model's delay probability (0-1)
        cost_of_product: Product value ($)
        mode_of_shipment: Ship / Flight / Road
        prediction: 1=predicted delayed, 0=predicted on-time
        
    Returns:
        Expected loss in USD
    """
    base = AVG_DELAY_PENALTY_USD * probability_delayed
    
    # High-value products have higher penalty
    if cost_of_product > 10000:
        base *= HIGH_VALUE_MULTIPLIER
    
    # Shipping mode penalty
    if mode_of_shipment == "Ship":
        base *= 1.12  # Sea freight more risky
    
    # Prediction confidence adjusts baseline
    if prediction == 1:
        return round(base, 2)
    else:
        return round(base * 0.35, 2)  # Residual risk even if predicted on-time


def recommend_interventions(
    shipment: Dict[str, Any],
    probability_delayed: float,
    expected_loss: float,
    prediction: int = 1,
) -> List[Dict[str, Any]]:
    """
    Recommend cost-justified interventions for this shipment.
    
    Only recommends actions where: (Expected Loss × Mitigation Rate) > Cost
    Returns interventions sorted by ROI (net benefit / cost).
    
    Args:
        shipment: Shipment feature dict
        probability_delayed: Model delay probability
        expected_loss: Calculated expected loss
        prediction: Binary prediction
        
    Returns:
        List of recommended interventions with ROI
    """
    recommendations = []
    
    # Only consider interventions if delay probability warrants it
    if probability_delayed < 0.35:
        return []
    
    cost_of_product = float(shipment.get("cost_of_the_product", 1000))
    mode_of_shipment = shipment.get("mode_of_shipment", "Ship")
    customer_rating = float(shipment.get("customer_rating", 3.0))
    prior_purchases = int(shipment.get("prior_purchases", 0))
    
    # Evaluate each intervention
    for action, cost in INTERVENTION_COSTS.items():
        mitigation_rate = MITIGATION_RATES.get(action, 0.0)
        loss_prevented = expected_loss * mitigation_rate
        net_benefit = loss_prevented - cost
        roi = (net_benefit / cost * 100) if cost > 0 else 0
        
        # Only recommend if ROI > 0 (benefit > cost)
        if net_benefit > 0:
            # Contextual filters for each action
            should_recommend = False
            priority = "P2"
            reason = ""
            
            if action == "expedite_to_flight":
                # Recommend for high-risk, sea shipments, high-value items
                if probability_delayed > 0.60 and mode_of_shipment == "Ship":
                    should_recommend = True
                    priority = "P1" if cost_of_product > 5000 else "P2"
                    reason = f"High delay risk ({probability_delayed*100:.0f}%) + sea route"
                    
            elif action == "manual_priority_sort":
                # Recommend for medium+ risk or high-value items
                if probability_delayed > 0.45:
                    should_recommend = True
                    priority = "P1" if cost_of_product > 8000 else "P2"
                    reason = f"Prevent sortation delays (P{priority[-1]})"
                    
            elif action == "customer_proactive_notification":
                # Recommend for loyal customers (high prior purchases) at any risk
                if prior_purchases > 5 or customer_rating > 4.0:
                    should_recommend = True
                    priority = "P2"
                    reason = "VIP customer retention"
                    
            elif action == "reroute_to_closer_warehouse":
                # Recommend for medium+ risk and specific warehouse blocks
                warehouse = shipment.get("warehouse_block", "A")
                if probability_delayed > 0.50 and warehouse in ("D", "E", "F"):
                    should_recommend = True
                    priority = "P1" if probability_delayed > 0.70 else "P2"
                    reason = f"Remote warehouse {warehouse} → reroute to closer hub"
            
            if should_recommend:
                recommendations.append({
                    "action": action,
                    "action_display": action.replace("_", " ").title(),
                    "cost_usd": round(cost, 2),
                    "loss_prevented_usd": round(loss_prevented, 2),
                    "net_benefit_usd": round(net_benefit, 2),
                    "roi_percent": round(roi, 1),
                    "priority": priority,
                    "reason": reason,
                })
    
    # Sort by net benefit descending (highest ROI first)
    recommendations.sort(key=lambda x: x["net_benefit_usd"], reverse=True)
    
    return recommendations[:3]  # Return top 3 recommendations


def calculate_intervention_summary(
    recommendations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Summarize total cost and benefit if all recommendations are implemented.
    
    Args:
        recommendations: List of recommendation dicts
        
    Returns:
        Summary dict with totals
    """
    if not recommendations:
        return {
            "total_cost": 0.0,
            "total_loss_prevented": 0.0,
            "total_net_benefit": 0.0,
            "implementation_feasible": False,
        }
    
    total_cost = sum(r["cost_usd"] for r in recommendations)
    total_loss_prevented = sum(r["loss_prevented_usd"] for r in recommendations)
    total_net_benefit = sum(r["net_benefit_usd"] for r in recommendations)
    
    return {
        "total_cost": round(total_cost, 2),
        "total_loss_prevented": round(total_loss_prevented, 2),
        "total_net_benefit": round(total_net_benefit, 2),
        "implementation_feasible": total_net_benefit > 0,
        "action_count": len(recommendations),
    }


class BatchInterventionOptimizer:
    """
    Solves: 'Given N shipments and a budget constraint, which shipments should we intervene on?'
    Uses greedy knapsack optimization: ROI-per-cost ranking.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def optimize(
        self,
        shipments: List[Dict[str, Any]],
        predictions: List[Dict[str, float]],
        budget: float,
        constraint: str = "maximize_net_benefit",
    ) -> Dict[str, Any]:
        """
        Select which shipments to intervene on, respecting budget constraint.
        
        Args:
            shipments: List of shipment dicts
            predictions: List of predictions (probability_delayed, etc.)
            budget: Max cost allowed for interventions ($)
            constraint: Optimization target ("maximize_net_benefit" or "maximize_roi")
            
        Returns:
            Optimization result with selected interventions
        """
        if not shipments or not predictions or budget <= 0:
            return {
                "selected_interventions": [],
                "total_cost": 0.0,
                "total_net_benefit": 0.0,
                "budget_used": 0.0,
                "budget_remaining": budget,
                "shipments_selected": 0,
            }
        
        # Build candidate list: (shipment_idx, intervention, roi_score)
        candidates = []
        
        for idx, (shipment, pred) in enumerate(zip(shipments, predictions)):
            prob = pred.get("probability_delayed", 0.0)
            
            if prob < 0.35:  # Skip low-risk
                continue
            
            expected_loss = calculate_expected_loss(
                prob,
                float(shipment.get("cost_of_the_product", 1000)),
                shipment.get("mode_of_shipment", "Ship"),
            )
            
            recs = recommend_interventions(shipment, prob, expected_loss)
            
            for rec in recs:
                roi_score = rec["net_benefit_usd"] / rec["cost_usd"] if rec["cost_usd"] > 0 else 0
                candidates.append({
                    "shipment_idx": idx,
                    "shipment_id": shipment.get("shipment_id", f"SHP-{idx}"),
                    "action": rec["action"],
                    "action_display": rec["action_display"],
                    "cost": rec["cost_usd"],
                    "net_benefit": rec["net_benefit_usd"],
                    "roi_score": roi_score,
                })
        
        # Sort by ROI (benefit-per-dollar)
        candidates.sort(key=lambda x: x["roi_score"], reverse=True)
        
        # Greedy selection: pick highest ROI until budget exhausted
        selected = []
        total_cost = 0.0
        total_benefit = 0.0
        
        for candidate in candidates:
            if total_cost + candidate["cost"] <= budget:
                selected.append(candidate)
                total_cost += candidate["cost"]
                total_benefit += candidate["net_benefit"]
        
        return {
            "selected_interventions": selected,
            "total_cost": round(total_cost, 2),
            "total_net_benefit": round(total_benefit, 2),
            "budget_used": round(total_cost, 2),
            "budget_remaining": round(budget - total_cost, 2),
            "shipments_selected": len(selected),
            "avg_roi_percent": round(
                sum(c["roi_score"] for c in selected) / len(selected) * 100, 1
            ) if selected else 0.0,
        }
