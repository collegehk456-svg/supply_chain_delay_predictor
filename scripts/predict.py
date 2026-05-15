"""Prediction CLI for the Supply Chain Delay Predictor."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

# Ensure the project root is on sys.path for src package imports
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from src.ml_pipeline.models.predictor import ModelPredictor


def load_json_input(path: Path) -> Dict[str, Any]:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Run a single prediction using the saved pipeline.")
    parser.add_argument(
        '--pipeline-path',
        type=str,
        default='models/production/full_pipeline.pkl',
        help='Path to the serialized prediction pipeline.'
    )
    parser.add_argument(
        '--input-file',
        type=str,
        required=True,
        help='Path to a JSON file containing a single shipment payload.'
    )
    args = parser.parse_args()

    pipeline_path = Path(args.pipeline_path)
    if not pipeline_path.exists():
        raise FileNotFoundError(f'Pipeline file not found: {pipeline_path}')

    predictor = ModelPredictor.load(str(pipeline_path))
    payload = load_json_input(Path(args.input_file))
    result = predictor.predict_single(payload)

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
