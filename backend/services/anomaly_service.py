"""
Anomaly Detection Service
Real-time shipment anomaly detection using Isolation Forest + statistical thresholds.
Provides risk scoring, pattern detection, and intelligent alerting.
"""

import logging
import random
import math
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from pathlib import Path

logger = logging.getLogger(__name__)


BASELINE_STATS = {
    "discount_offered": {"mean": 13.4, "std": 15.1, "high_risk_threshold": 35.0},
    "weight_in_gms": {"mean": 3634, "std": 1768, "high_risk_threshold": 6000},
    "customer_care_calls": {"mean": 3.8, "std": 1.8, "high_risk_threshold": 7},
    "cost_of_the_product": {"mean": 3234, "std": 1545, "high_risk_threshold": 8000},
    "prior_purchases": {"mean": 3.5, "std": 1.5, "low_risk_threshold": 2},
}

SHIPMENT_TEMPLATES = [
    {"warehouse_block": "A", "mode_of_shipment": "Ship",   "customer_care_calls": 2, "customer_rating": 4.0, "cost_of_the_product": 3200, "prior_purchases": 5, "product_importance": "Medium", "gender": "M", "discount_offered": 8,  "weight_in_gms": 2100},
    {"warehouse_block": "B", "mode_of_shipment": "Flight", "customer_care_calls": 1, "customer_rating": 4.5, "cost_of_the_product": 6500, "prior_purchases": 7, "product_importance": "High",   "gender": "F", "discount_offered": 5,  "weight_in_gms": 1800},
    {"warehouse_block": "F", "mode_of_shipment": "Ship",   "customer_care_calls": 6, "customer_rating": 2.0, "cost_of_the_product": 1200, "prior_purchases": 1, "product_importance": "Low",    "gender": "M", "discount_offered": 48, "weight_in_gms": 5200},
    {"warehouse_block": "D", "mode_of_shipment": "Road",   "customer_care_calls": 4, "customer_rating": 3.0, "cost_of_the_product": 2800, "prior_purchases": 3, "product_importance": "Medium", "gender": "F", "discount_offered": 22, "weight_in_gms": 3800},
    {"warehouse_block": "C", "mode_of_shipment": "Flight", "customer_care_calls": 2, "customer_rating": 4.5, "cost_of_the_product": 9200, "prior_purchases": 8, "product_importance": "High",   "gender": "M", "discount_offered": 3,  "weight_in_gms": 1500},
    {"warehouse_block": "E", "mode_of_shipment": "Ship",   "customer_care_calls": 7, "customer_rating": 1.5, "cost_of_the_product": 890,  "prior_purchases": 1, "product_importance": "Low",    "gender": "F", "discount_offered": 55, "weight_in_gms": 6800},
    {"warehouse_block": "A", "mode_of_shipment": "Road",   "customer_care_calls": 3, "customer_rating": 3.5, "cost_of_the_product": 4100, "prior_purchases": 4, "product_importance": "Medium", "gender": "M", "discount_offered": 15, "weight_in_gms": 2900},
    {"warehouse_block": "B", "mode_of_shipment": "Ship",   "customer_care_calls": 5, "customer_rating": 2.5, "cost_of_the_product": 1800, "prior_purchases": 2, "product_importance": "Low",    "gender": "F", "discount_offered": 33, "weight_in_gms": 4400},
]

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
    "London", "Berlin", "Paris", "Tokyo", "Singapore",
    "Dubai", "Mumbai", "Sydney", "Toronto", "São Paulo",
]

ALERT_TEMPLATES = [
    {"severity": "CRITICAL", "icon": "🔴", "message": "Extreme discount ({discount:.0f}%) — high surge risk", "color": "#ef4444"},
    {"severity": "HIGH",     "icon": "🟠", "message": "Heavy package ({weight:.0f}g) via Ship — delay likely",  "color": "#f97316"},
    {"severity": "HIGH",     "icon": "🟠", "message": "New customer with {calls} support calls — flag for review", "color": "#f97316"},
    {"severity": "MEDIUM",   "icon": "🟡", "message": "Remote warehouse block {block} — slower dispatch",         "color": "#eab308"},
    {"severity": "LOW",      "icon": "🟢", "message": "Shipment profile within normal parameters",                "color": "#22c55e"},
]


class AnomalyDetectionService:
    """
    Production-grade anomaly detection for shipment streams.
    Uses Isolation Forest + rule-based statistical thresholds.
    """

    def __init__(self):
        self.model: Optional[IsolationForest] = None
        self.scaler: Optional[StandardScaler] = None
        self.feature_cols = [
            "customer_care_calls", "customer_rating", "cost_of_the_product",
            "prior_purchases", "discount_offered", "weight_in_gms",
        ]
        self._live_stream: List[Dict] = []
        self._alerts: List[Dict] = []
        self._anomaly_count = 0
        self._total_scored = 0

    def train(self, df: pd.DataFrame) -> None:
        X = df[self.feature_cols].values
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        self.model = IsolationForest(
            n_estimators=100, contamination=0.08,
            random_state=42, n_jobs=-1
        )
        self.model.fit(X_scaled)
        logger.info("Isolation Forest trained on %d samples", len(df))

    def score_shipment(self, shipment: Dict[str, Any]) -> Dict[str, Any]:
        self._total_scored += 1
        feat_vec = np.array([[
            shipment.get("customer_care_calls", 3),
            shipment.get("customer_rating", 3.5),
            shipment.get("cost_of_the_product", 3000),
            shipment.get("prior_purchases", 3),
            shipment.get("discount_offered", 10),
            shipment.get("weight_in_gms", 3000),
        ]])

        iso_anomaly = False
        iso_score   = 0.0
        if self.model and self.scaler:
            scaled = self.scaler.transform(feat_vec)
            iso_score   = float(-self.model.score_samples(scaled)[0])
            iso_anomaly = bool(self.model.predict(scaled)[0] == -1)

        stat_flags = self._statistical_check(shipment)
        risk_score = self._compute_risk(shipment, iso_score, stat_flags)
        risk_level = self._risk_level(risk_score)
        alert      = self._build_alert(shipment, risk_level, stat_flags)

        if risk_level in ("CRITICAL", "HIGH"):
            self._anomaly_count += 1

        result = {
            "shipment_id": f"SHP-{random.randint(10000,99999)}",
            "timestamp": datetime.utcnow().isoformat(),
            "risk_score": round(float(risk_score * 100), 1),
            "risk_level": str(risk_level),
            "is_anomaly": bool(iso_anomaly or risk_score > 0.6),
            "isolation_score": round(float(iso_score), 4),
            "statistical_flags": [str(f) for f in stat_flags],
            "alert": alert,
            "shipment": {k: (float(v) if isinstance(v, (np.floating, np.integer)) else v) for k, v in shipment.items()},
        }
        return result

    def _statistical_check(self, s: Dict) -> List[str]:
        flags = []
        if s.get("discount_offered", 0) > 35:
            flags.append(f"Extreme discount: {s['discount_offered']:.0f}%")
        if s.get("weight_in_gms", 0) > 5500:
            flags.append(f"Very heavy: {s['weight_in_gms']:.0f}g")
        if s.get("customer_care_calls", 0) >= 7:
            flags.append(f"High support calls: {s['customer_care_calls']}")
        if s.get("prior_purchases", 5) < 2:
            flags.append("New customer — higher error risk")
        if s.get("customer_rating", 5) < 2.0:
            flags.append(f"Very low rating: {s['customer_rating']:.1f}")
        if s.get("warehouse_block", "A") in ("E", "F") and s.get("mode_of_shipment") == "Ship":
            flags.append("Remote block + Ship: high delay combo")
        return flags

    def _compute_risk(self, s: Dict, iso_score: float, flags: List[str]) -> float:
        risk = 0.0
        d = s.get("discount_offered", 0)
        if d > 50:   risk += 0.45
        elif d > 35: risk += 0.30
        elif d > 20: risk += 0.15
        w = s.get("weight_in_gms", 0)
        if w > 6000: risk += 0.20
        elif w > 4000: risk += 0.12
        if s.get("customer_care_calls", 0) >= 7: risk += 0.15
        elif s.get("customer_care_calls", 0) >= 5: risk += 0.08
        if s.get("prior_purchases", 5) < 2: risk += 0.10
        if s.get("customer_rating", 5) < 2: risk += 0.08
        if iso_score > 0.5: risk += 0.20
        elif iso_score > 0.3: risk += 0.10
        risk += len(flags) * 0.05
        return min(risk, 1.0)

    def _risk_level(self, score: float) -> str:
        if score >= 0.70: return "CRITICAL"
        if score >= 0.45: return "HIGH"
        if score >= 0.25: return "MEDIUM"
        return "LOW"

    def _build_alert(self, s: Dict, risk: str, flags: List[str]) -> Dict:
        colors = {"CRITICAL": "#ef4444", "HIGH": "#f97316", "MEDIUM": "#eab308", "LOW": "#22c55e"}
        icons  = {"CRITICAL": "🔴",       "HIGH": "🟠",       "MEDIUM": "🟡",      "LOW": "🟢"}
        if flags:
            msg = flags[0]
        elif risk == "CRITICAL":
            msg = "Multiple critical risk factors detected"
        elif risk == "HIGH":
            msg = "Elevated delay risk — intervention recommended"
        elif risk == "MEDIUM":
            msg = "Moderate risk — monitor closely"
        else:
            msg = "Shipment within normal parameters"
        return {"severity": risk, "message": msg, "color": colors[risk], "icon": icons[risk]}

    def simulate_live_stream(self, n: int = 15) -> List[Dict]:
        stream = []
        now = datetime.utcnow()
        for i in range(n):
            base = random.choice(SHIPMENT_TEMPLATES).copy()
            # Inject realistic noise
            base["discount_offered"] = max(0, min(65, base["discount_offered"] + random.uniform(-8, 8)))
            base["weight_in_gms"]    = max(200, base["weight_in_gms"] + random.randint(-500, 500))
            base["customer_care_calls"] = max(0, min(10, base["customer_care_calls"] + random.randint(-1, 2)))
            scored = self.score_shipment(base)
            scored["origin"]      = random.choice(CITIES)
            scored["destination"] = random.choice([c for c in CITIES if c != scored["origin"]])
            scored["eta_hours"]   = random.randint(12, 96)
            scored["timestamp"]   = (now - timedelta(minutes=i * 3)).isoformat()
            stream.append(scored)
        self._live_stream = stream
        return stream

    def get_executive_summary(self) -> Dict[str, Any]:
        stream = self._live_stream or self.simulate_live_stream(20)
        scores = [s["risk_score"] for s in stream]
        critical = sum(1 for s in stream if s["risk_level"] == "CRITICAL")
        high     = sum(1 for s in stream if s["risk_level"] == "HIGH")
        medium   = sum(1 for s in stream if s["risk_level"] == "MEDIUM")
        low      = sum(1 for s in stream if s["risk_level"] == "LOW")
        avg_risk = sum(scores) / len(scores)

        if avg_risk > 55:
            headline = "⚠️ ELEVATED SYSTEM RISK — Immediate Action Required"
            summary  = (
                f"The live shipment stream shows {critical} critical and {high} high-risk shipments. "
                "Primary drivers are excessive discounting and heavy-weight packages via sea freight. "
                "Recommend activating surge protocols and expediting flagged shipments."
            )
        elif avg_risk > 35:
            headline = "🟡 MODERATE RISK — Monitor Active Alerts"
            summary  = (
                f"System risk is elevated with {high} high-risk and {medium} medium-risk shipments. "
                "Discount-driven surge is the leading concern. "
                "Recommend proactive customer notifications for flagged orders."
            )
        else:
            headline = "✅ SYSTEM HEALTHY — Operations Nominal"
            summary  = (
                f"Current shipment stream is within acceptable parameters. "
                f"{low} shipments are low-risk. Continue standard monitoring protocols."
            )

        top_anomalies = sorted(stream, key=lambda x: x["risk_score"], reverse=True)[:3]

        return {
            "headline": headline,
            "summary": summary,
            "avg_risk_score": round(avg_risk, 1),
            "critical_count": critical,
            "high_count": high,
            "medium_count": medium,
            "low_count": low,
            "total_monitored": len(stream),
            "top_anomalies": top_anomalies,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_warehouse_risk_map(self) -> List[Dict]:
        blocks = ["A", "B", "C", "D", "E", "F"]
        delay_rates = {"A": 52, "B": 55, "C": 58, "D": 63, "E": 68, "F": 65}
        volume      = {"A": 1833, "B": 1833, "C": 1833, "D": 1834, "E": 1000, "F": 3666}
        return [
            {
                "block": b,
                "delay_rate": delay_rates[b] + random.uniform(-2, 2),
                "volume": volume[b],
                "risk_score": (delay_rates[b] - 50) / 25,
                "active_shipments": random.randint(12, 80),
            }
            for b in blocks
        ]

    @property
    def stats(self) -> Dict:
        return {
            "total_scored": self._total_scored,
            "anomalies_detected": self._anomaly_count,
            "anomaly_rate": round(self._anomaly_count / max(self._total_scored, 1) * 100, 1),
            "model_trained": self.model is not None,
        }
