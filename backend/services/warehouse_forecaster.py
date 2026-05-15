"""
Warehouse Load Forecaster
Real-time warehouse capacity monitoring and bottleneck detection.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# Warehouse capacity (grams)
WAREHOUSE_CAPACITY = {
    "A": 500000,   # 500 kg
    "B": 550000,   # 550 kg
    "C": 480000,   # 480 kg
    "D": 420000,   # 420 kg (remote, smaller)
    "E": 410000,   # 410 kg (remote, smaller)
    "F": 430000,   # 430 kg (remote, smaller)
}

# Risk thresholds
UTILIZATION_THRESHOLD_WARNING = 0.75  # 75% → YELLOW
UTILIZATION_THRESHOLD_CRITICAL = 0.85  # 85% → RED


class WarehouseLoadForecaster:
    """
    Forecasts real-time warehouse load and triggers alerts when capacity is exceeded.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recent_predictions = []  # Store recent predictions for load calculation
    
    def add_prediction(self, shipment: Dict[str, Any], probability_delayed: float):
        """
        Add a prediction to the load forecast queue.
        
        Args:
            shipment: Shipment dict with warehouse_block and weight_in_gms
            probability_delayed: Model's delay probability
        """
        self.recent_predictions.append({
            "warehouse_block": shipment.get("warehouse_block", "A"),
            "weight_in_gms": float(shipment.get("weight_in_gms", 1000)),
            "probability_delayed": probability_delayed,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Keep only last 1000 predictions (rolling window)
        if len(self.recent_predictions) > 1000:
            self.recent_predictions = self.recent_predictions[-1000:]
    
    def forecast_load(self) -> Dict[str, Any]:
        """
        Calculate current warehouse utilization and alert status.
        
        Returns:
            Dict with utilization per warehouse and alerts
        """
        load_by_warehouse = {wb: 0 for wb in WAREHOUSE_CAPACITY.keys()}
        
        # Sum weights by warehouse
        for pred in self.recent_predictions:
            wb = pred["warehouse_block"]
            if wb in load_by_warehouse:
                load_by_warehouse[wb] += pred["weight_in_gms"]
        
        # Calculate utilization and risk tier
        forecast = {
            "timestamp": datetime.utcnow().isoformat(),
            "warehouses": {},
            "alerts": [],
            "recommendations": [],
        }
        
        for warehouse_block, capacity in WAREHOUSE_CAPACITY.items():
            load = load_by_warehouse[warehouse_block]
            utilization = load / capacity if capacity > 0 else 0
            
            # Determine risk tier
            if utilization >= UTILIZATION_THRESHOLD_CRITICAL:
                risk_tier = "CRITICAL"
                risk_color = "#ef4444"
            elif utilization >= UTILIZATION_THRESHOLD_WARNING:
                risk_tier = "WARNING"
                risk_color = "#f97316"
            else:
                risk_tier = "NORMAL"
                risk_color = "#22c55e"
            
            forecast["warehouses"][warehouse_block] = {
                "load_grams": round(load, 0),
                "capacity_grams": capacity,
                "utilization_percent": round(utilization * 100, 1),
                "risk_tier": risk_tier,
                "risk_color": risk_color,
            }
            
            # Generate alerts
            if utilization >= UTILIZATION_THRESHOLD_CRITICAL:
                forecast["alerts"].append({
                    "warehouse": warehouse_block,
                    "severity": "CRITICAL",
                    "message": f"Warehouse {warehouse_block} at {utilization*100:.0f}% capacity. IMMEDIATE ACTION REQUIRED.",
                    "action": f"Reroute new shipments from Block {warehouse_block} to less-loaded blocks (A, B, C)",
                })
                forecast["recommendations"].append({
                    "warehouse": warehouse_block,
                    "action": "reroute_high_discount_items",
                    "description": f"Auto-distribute high-discount shipments from Block {warehouse_block} to A or B",
                    "priority": "P1",
                })
            elif utilization >= UTILIZATION_THRESHOLD_WARNING:
                forecast["alerts"].append({
                    "warehouse": warehouse_block,
                    "severity": "WARNING",
                    "message": f"Warehouse {warehouse_block} at {utilization*100:.0f}% capacity. Monitor closely.",
                    "action": f"Monitor Block {warehouse_block}. Prepare reroute if exceeds 85%.",
                })
        
        return forecast
    
    def get_reroute_suggestion(
        self,
        from_warehouse: str,
        shipment_weight: float,
    ) -> Optional[str]:
        """
        Suggest a better warehouse if source warehouse is overloaded.
        
        Args:
            from_warehouse: Current warehouse block
            shipment_weight: Shipment weight (grams)
            
        Returns:
            Suggested warehouse block, or None
        """
        # Calculate current load
        load_by_warehouse = {wb: 0 for wb in WAREHOUSE_CAPACITY.keys()}
        for pred in self.recent_predictions:
            wb = pred["warehouse_block"]
            if wb in load_by_warehouse:
                load_by_warehouse[wb] += pred["weight_in_gms"]
        
        # Check if origin is overloaded
        origin_capacity = WAREHOUSE_CAPACITY.get(from_warehouse, 500000)
        origin_utilization = load_by_warehouse[from_warehouse] / origin_capacity
        
        if origin_utilization < UTILIZATION_THRESHOLD_WARNING:
            return None  # Origin is fine, no reroute needed
        
        # Find the least-loaded warehouse
        best_warehouse = None
        best_utilization = 1.0
        
        for wb, capacity in WAREHOUSE_CAPACITY.items():
            if wb == from_warehouse:
                continue  # Skip origin
            
            potential_load = load_by_warehouse[wb] + shipment_weight
            utilization = potential_load / capacity
            
            if utilization < best_utilization:
                best_warehouse = wb
                best_utilization = utilization
        
        return best_warehouse
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a high-level summary of warehouse health.
        
        Returns:
            Summary dict with key metrics
        """
        forecast = self.forecast_load()
        
        warehouses_status = forecast["warehouses"]
        critical_count = sum(1 for w in warehouses_status.values() if w["risk_tier"] == "CRITICAL")
        warning_count = sum(1 for w in warehouses_status.values() if w["risk_tier"] == "WARNING")
        normal_count = 6 - critical_count - warning_count
        
        avg_utilization = sum(w["utilization_percent"] for w in warehouses_status.values()) / 6
        
        return {
            "timestamp": forecast["timestamp"],
            "total_warehouses": 6,
            "critical": critical_count,
            "warning": warning_count,
            "normal": normal_count,
            "average_utilization_percent": round(avg_utilization, 1),
            "alert_count": len(forecast["alerts"]),
            "system_health": "HEALTHY" if critical_count == 0 else "DEGRADED" if warning_count > 2 else "NORMAL",
        }
