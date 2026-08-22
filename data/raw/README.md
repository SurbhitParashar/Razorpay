# Synthetic Payment Events

This directory contains the versioned raw synthetic payment dataset used by RecoverAI.

## Dataset

- Records: 50,000
- Time range: January 2026 to December 2026
- Generation seed: 42
- Format: CSV
- Versioning: DVC

## Reproducibility

The dataset is generated deterministically from the configuration in:

`scripts/generate_data.py`

Running the generator with the same configuration and seed produces the same dataset.

## Important

This dataset contains synthetic data only. No production customer, payment, or merchant information is included.