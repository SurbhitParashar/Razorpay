from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class TemporalSplit:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def temporal_split(
    dataframe: pd.DataFrame,
    train_end: str = "2026-09-30",
    validation_end: str = "2026-11-30",
) -> TemporalSplit:
    frame = dataframe.copy()

    frame["occurred_at"] = pd.to_datetime(
        frame["occurred_at"],
        utc=True,
    )

    train_cutoff = pd.Timestamp(train_end, tz="UTC")
    validation_cutoff = pd.Timestamp(validation_end, tz="UTC")

    train = frame[frame["occurred_at"] <= train_cutoff].copy()

    validation = frame[
        (frame["occurred_at"] > train_cutoff) & (frame["occurred_at"] <= validation_cutoff)
    ].copy()

    test = frame[frame["occurred_at"] > validation_cutoff].copy()

    if train.empty or validation.empty or test.empty:
        raise ValueError("Temporal split produced an empty partition.")

    if train["occurred_at"].max() >= validation["occurred_at"].min():
        raise ValueError("Train and validation periods overlap.")

    if validation["occurred_at"].max() >= test["occurred_at"].min():
        raise ValueError("Validation and test periods overlap.")

    return TemporalSplit(
        train=train,
        validation=validation,
        test=test,
    )
