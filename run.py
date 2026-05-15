#!/usr/bin/env python
"""
SmartShip AI — one-command launcher for hackathon demos.
Starts FastAPI backend and Streamlit dashboard.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    os.chdir(ROOT)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    data = ROOT / "data" / "raw" / "train.csv"
    pipeline = ROOT / "models" / "production" / "full_pipeline.pkl"
    if not data.exists() and (ROOT / "Train.csv").exists():
        data.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy(ROOT / "Train.csv", data)
    if not pipeline.exists():
        print("Training model (first run)…")
        subprocess.check_call([
            sys.executable, "scripts/train.py",
            "--data-path", str(data),
            "--output-path", "models/production/model.pkl",
        ])

    env = os.environ.copy()
    env.setdefault("API_URL", "http://localhost:8000")

    print("Starting SmartShip API on http://localhost:8000 …")
    api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
        env=env,
        cwd=str(ROOT),
    )
    time.sleep(2)
    print("Starting SmartShip Dashboard on http://localhost:8501 …")
    try:
        subprocess.call(
            [sys.executable, "-m", "streamlit", "run", "frontend/main.py", "--server.port", "8501"],
            env=env,
            cwd=str(ROOT),
        )
    finally:
        api.terminate()
        api.wait(timeout=5)


if __name__ == "__main__":
    main()
