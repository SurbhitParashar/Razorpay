from pathlib import Path

import pandas as pd

from recoverai.data.validation import validate_dataset

DATASET_PATH = Path("data/raw/payments.csv")


def test_raw_dataset_exists() -> None:
    assert DATASET_PATH.exists()


def test_raw_dataset_passes_validation() -> None:
    validate_dataset(DATASET_PATH)


def test_raw_dataset_has_expected_volume() -> None:
    dataframe = pd.read_csv(DATASET_PATH)

    assert len(dataframe) == 50_000


def test_recovery_rate_is_not_extreme() -> None:
    dataframe = pd.read_csv(DATASET_PATH)

    recovery_rate = dataframe["recovered"].mean()

    assert 0.05 < recovery_rate < 0.95


def test_recovered_revenue_is_bounded() -> None:
    dataframe = pd.read_csv(DATASET_PATH)

    assert (dataframe["recovered_amount_inr"] <= dataframe["amount_inr"]).all()
