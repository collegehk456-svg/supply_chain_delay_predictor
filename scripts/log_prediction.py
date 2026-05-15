"""Append prediction to logs/prediction_log.csv for drift monitoring."""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

LOG_PATH = Path("logs/prediction_log.csv")
FIELDS = ["timestamp", "prediction", "probability_delayed", "risk_tier", "priority_score"]


def log_prediction(
    prediction: int,
    probability_delayed: float,
    risk_tier: str = "",
    priority_score: float = 0.0,
) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_header = not LOG_PATH.exists()
    with open(LOG_PATH, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            w.writeheader()
        w.writerow({
            "timestamp": datetime.utcnow().isoformat(),
            "prediction": prediction,
            "probability_delayed": probability_delayed,
            "risk_tier": risk_tier,
            "priority_score": priority_score,
        })
