"""Backward compatibility shim for old ml_pipeline imports."""

import os
from pathlib import Path

# Allow legacy imports using ml_pipeline.* to work after moving code to src/ml_pipeline
__path__.append(str(Path(__file__).resolve().parent.parent / 'src' / 'ml_pipeline'))
