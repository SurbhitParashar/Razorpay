# RecoverAI

AI-powered revenue recovery agent for merchants.

## Status

Active development

## Track

Track 03: AI Revenue Recovery

## Problem

RecoverAI is being built to detect revenue at risk, estimate recovery likelihood, propose bounded recovery actions, execute approved actions through Razorpay Test Mode, and measure recovered revenue across a batch.

## Engineering Goals

- Reproducible ML pipeline
- DVC-managed datasets and models
- Deterministic policy enforcement
- Bounded agent actions
- Complete audit trail
- Automated testing
- CI validation
- Containerized deployment
- Measured recovery performance

## Technology

Current foundation:

- Python 3.13
- uv
- DVC
- Ruff
- MyPy
- Pytest
- pre-commit

Application dependencies will be added incrementally as each system component is implemented.

## Repository Structure

```text
data/        Data artifacts
docs/        Technical documentation
configs/     Configuration
metrics/     Evaluation metrics
models/      Model artifacts
scripts/     Utility scripts
src/         Application source
tests/       Automated tests