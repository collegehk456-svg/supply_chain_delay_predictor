"""Evaluation CLI for the Supply Chain Delay Predictor."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

# Ensure the project root is on sys.path for src package imports
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pandas as pd
from src.ml_pipeline.models.predictor import ModelPredictor
from src.ml_pipeline.models.evaluator import ModelEvaluator


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [col.replace('.', '_').replace('/', '_') for col in df.columns]
    return df


def detect_target(df: pd.DataFrame) -> str:
    candidates = ['Reached_on_Time_Y_N', 'Reached_on_Time_Y_N']
    candidates += [col for col in df.columns if df[col].dtype in ['int64', 'int32'] and set(df[col].dropna().unique()).issubset({0, 1})]
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    raise ValueError('Unable to identify target column in evaluation data.')


def main():
    parser = argparse.ArgumentParser(description='Evaluate the saved prediction pipeline on labeled data.')
    parser.add_argument(
        '--pipeline-path',
        type=str,
        default='models/production/full_pipeline.pkl',
        help='Path to the serialized prediction pipeline.'
    )
    parser.add_argument(
        '--data-path',
        type=str,
        default='data/raw/train.csv',
        help='Path to evaluation CSV data with ground truth labels.'
    )
    parser.add_argument(
        '--output-path',
        type=str,
        default='artifacts/evaluation_metrics.json',
        help='Path to save the evaluation results.'
    )
    args = parser.parse_args()

    predictor = ModelPredictor.load(args.pipeline_path)
    df = load_data(Path(args.data_path))
    target_col = detect_target(df)
    df = df.rename(columns={target_col: 'Reached_on_Time_Y_N'})

    y_true = df['Reached_on_Time_Y_N']
    X = df.drop(columns=['Reached_on_Time_Y_N'])

    predictions = []
    probabilities = []
    for _, row in X.iterrows():
        result = predictor.predict_single(row.to_dict())
        predictions.append(result['prediction'])
        probabilities.append(result['probability_delayed'])

    evaluator = ModelEvaluator()
    proba_matrix = np.vstack([1.0 - np.array(probabilities), np.array(probabilities)]).T
    metrics = evaluator.evaluate(y_true, pd.Series(predictions), proba_matrix)

    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({k: float(v) for k, v in metrics.items() if k != 'confusion_matrix'}, f, indent=2)

    print('Evaluation complete')
    print(json.dumps(metrics, indent=2, default=str))
    print(f'Metrics saved to {output_path}')


if __name__ == '__main__':
    main()
