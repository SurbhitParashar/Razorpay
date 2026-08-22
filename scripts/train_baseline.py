import json
from decimal import Decimal
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from recoverai.ml.evaluate import (
    evaluate_business_impact,
    evaluate_predictions,
)
from recoverai.ml.features import build_features
from recoverai.ml.split import temporal_split
from recoverai.ml.threshold import select_threshold
from recoverai.ml.train import build_pipeline

DATA_PATH = Path("data/raw/payments.csv")
MODEL_PATH = Path("models/recovery_baseline.joblib")
METRICS_PATH = Path("metrics/baseline.json")


def main() -> None:
    params = yaml.safe_load(Path("params.yaml").read_text(encoding="utf-8"))
    dataframe = pd.read_csv(DATA_PATH)

    intervention_cost = Decimal(str(params["economics"]["intervention_cost_inr"]))

    split = temporal_split(
        dataframe,
        train_end=params["split"]["train_end"],
        validation_end=params["split"]["validation_end"],
    )

    train_features = build_features(split.train)
    validation_features = build_features(split.validation)
    test_features = build_features(split.test)

    pipeline = build_pipeline(
        max_iter=params["model"]["max_iter"],
        class_weight=params["model"]["class_weight"],
        random_state=params["model"]["random_state"],
    )

    pipeline.fit(
        train_features.X,
        train_features.y,
    )

    validation_probabilities = pipeline.predict_proba(validation_features.X)[:, 1]

    test_probabilities = pipeline.predict_proba(test_features.X)[:, 1]

    validation_metrics = evaluate_predictions(
        validation_features.y.to_numpy(),
        validation_probabilities,
    )
    thresholds = np.arange(0.30, 0.71, 0.05)

    selection = select_threshold(
        probabilities=validation_probabilities,
        actual_recovery=split.validation["recovered"].to_numpy(),
        payment_amounts=split.validation["amount_inr"].to_numpy(),
        thresholds=thresholds,
        intervention_cost_inr=intervention_cost,
    )

    test_metrics = evaluate_predictions(
        test_features.y.to_numpy(),
        test_probabilities,
    )

    business_metrics = evaluate_business_impact(
        split.test,
        test_probabilities,
        threshold=selection.threshold,
    )

    metrics = {
        "validation": validation_metrics,
        "test": test_metrics,
        "business": business_metrics,
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)

    import joblib

    joblib.dump(pipeline, MODEL_PATH)

    METRICS_PATH.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
