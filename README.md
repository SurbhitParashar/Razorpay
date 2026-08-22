# RecoverAI

RecoverAI is an AI revenue-recovery system for Razorpay merchants. It identifies failed or at-risk payments that are economically worth recovering, executes a bounded recovery action such as creating a Razorpay payment link, persists idempotent state, and reports actual recovered revenue only after a successful recovery outcome is observed.

In one line: RecoverAI turns failed payments into a measurable, policy-gated recovery workflow instead of a manual spreadsheet chase.

Built for the Razorpay AI Buildathon, this project focuses on the part that matters most to a payments company: finding recoverable money, acting safely, and measuring rupees recovered.

## Highlights

- Built a payments-safe AI workflow, not a generic chatbot.
- Used ML to prioritize failed payments by recovery probability and business value.
- Added policy-gated execution so payment actions stay bounded, idempotent, and auditable.
- Used production-grade practices: DVC MLOps, uv, FastAPI, Razorpay SDK, SQLite state, Docker, strict MyPy, Ruff, pre-commit, and pytest.
- Measured impact in recovered revenue, not only model accuracy.

## Why This Matters

Merchants lose revenue when payments fail, remain pending, or require customer action. Today that loop often needs manual inspection:

- identify failed payments
- understand whether the customer is likely to complete payment
- decide whether follow-up is worth the cost
- create or resend a payment request
- track whether the money actually came back

RecoverAI automates that loop with a controlled architecture. The system does not blindly retry every payment. It estimates recovery probability, applies economics, enforces safety limits, creates a payment-link recovery action when allowed, and records outcomes separately from action execution.

The key business definition is strict:

> A payment is considered recovered only when an initially failed or at-risk transaction later reaches a successful paid state attributable to a RecoverAI intervention.

Creating a payment link is an action. It is not counted as recovered revenue until a paid outcome is recorded.

## Architecture Alignment

The current implementation is closely aligned with the target Razorpay-safe recovery architecture.

| Target architecture | Current implementation |
| --- | --- |
| Transaction ingestion | FastAPI request schemas and synthetic payment dataset model the recoverable transaction input. Full webhook ingestion is the next production step. |
| Feature engineering | `src/recoverai/ml/features.py` builds numerical and categorical ML features from payment and customer history. |
| Recovery ML model | Scikit-learn pipeline predicts recovery probability using payment method, failure class, customer history, merchant failure rate, attempt number, and amount behavior. |
| Agent decision engine | `RecoveryAgent` evaluates threshold and expected net value before deciding whether intervention is justified. |
| Policy / safety gate | `RecoveryExecutor` enforces probability threshold, max retry count, max recovery amount, idempotency, and dry-run behavior. |
| Razorpay tool execution | `RazorpayPaymentLinkProvider` integrates with Razorpay payment links in test-mode style; a fake provider supports deterministic tests. |
| Outcome observed | `/v1/recovery-outcomes` records paid, unpaid, failed, or expired outcomes. |
| Audit and state | SQLite-backed state persists recoveries, payment links, and outcomes with idempotency keys. |
| Business metrics | `/v1/recovery-metrics` reports attempted count, successful recoveries, failed recoveries, recovered revenue, and recovery rate. |

The only production gap is that live Razorpay webhook ingestion is not yet a full service. The code already has the provider boundary, state model, and outcome API needed to add it cleanly.

## System Flow

```text
Failed / at-risk payment
        |
        v
Feature engineering
        |
        v
Recovery ML model: P(recovery)
        |
        v
Agent decision engine
  - threshold check
  - expected net value check
        |
        v
Policy-gated executor
  - max amount
  - max retries
  - idempotency
  - durable state
        |
        +---- no action / stopped / skipped
        |
        +---- payment-link execution
                 |
                 v
          Razorpay provider
                 |
                 v
          outcome recorded
                 |
                 v
          recovery metrics
```

## What RecoverAI Solves

Example merchant payments:

| Payment | Amount | Status | Customer history | RecoverAI behavior |
| --- | ---: | --- | --- | --- |
| P001 | INR 4,999 | Failed | 4 previous successes | High-confidence recovery candidate |
| P002 | INR 799 | Failed | Weak history | Recover only if economics pass |
| P003 | INR 8,999 | Pending | 3 previous successes | Eligible for payment-link recovery |
| P004 | INR 1,499 | Failed | 2 recent failures | Likely skip or stop based on risk |

RecoverAI answers five practical questions:

1. Which failed payments are worth trying to recover?
2. Is expected recovered value higher than intervention cost?
3. Which bounded action should be executed?
4. How do we avoid duplicate recovery attempts?
5. How much revenue was actually recovered?

## Core Design Decisions

### 1. Recovery Is Measured, Not Assumed

Payment-link creation returns `recovered_amount_inr = 0`. Revenue is counted only when an outcome is recorded as `paid`.

This avoids fake recovery numbers and keeps the system honest for the metric Razorpay cares about most: recovered money.

### 2. Bounded Autonomy

The recovery agent does not receive unrestricted payment powers. Actions go through an executor and policy checks:

- recovery probability must meet threshold
- expected net value must be positive
- amount must be below merchant safety limit
- attempt number must be within retry limits
- duplicate requests must be skipped through idempotency
- execution state must survive process restarts

This is the difference between an AI demo and a payments-safe workflow.

### 3. Payment Links Are an Execution Mechanism

RecoverAI supports a payment-link provider interface:

- `FakePaymentLinkProvider` for deterministic local testing
- `RazorpayPaymentLinkProvider` for Razorpay payment-link creation

The executor can use the provider when configured, while the recovery domain remains separate from the external API.

### 4. Durable Idempotency

The same payment should not be recovered twice. RecoverAI uses idempotency keys such as:

```text
recoverai:<payment_id>
recoverai:<payment_id>:outcome
```

SQLite persists:

- successful gateway recoveries
- created payment links
- observed recovery outcomes

This keeps behavior consistent across repeated API calls and service restarts.

### 5. MLOps and Reproducibility

The ML training flow is tracked with DVC:

- dataset dependency: `data/raw/payments.csv`
- training command: `uv run python scripts/train_baseline.py`
- model output: `models/recovery_baseline.joblib`
- metrics output: `metrics/baseline.json`
- parameters: `params.yaml`

This gives the project a reproducible MLOps loop instead of an untracked notebook experiment.

## ML Model

The baseline model is a scikit-learn pipeline with:

- median imputation and scaling for numerical features
- most-frequent imputation and one-hot encoding for categorical features
- logistic regression with class balancing
- temporal train/validation/test split
- threshold selection based on business economics

Feature groups include:

- amount and attempt number
- payment method
- failure code and failure category
- customer tenure
- customer historical success rate
- previous failures in the last 30 days
- customer average amount
- amount versus customer average
- merchant 24-hour failure rate
- hour of day and day of week

Current baseline metrics:

| Split | Precision | Recall | PR AUC | ROC AUC | Brier score |
| --- | ---: | ---: | ---: | ---: | ---: |
| Validation | 0.773 | 0.753 | 0.823 | 0.832 | 0.167 |
| Test | 0.786 | 0.777 | 0.838 | 0.845 | 0.159 |

Business simulation on the test split:

| Metric | Value |
| --- | ---: |
| Intervention rate | 70.33% |
| Intervention count | 2,953 |
| Attempted recovery amount | INR 61.36 lakh |
| Simulated recovered revenue | INR 40.13 lakh |
| Actual recoveries | 2,029 |
| False positives | 924 |

## API

The service is exposed through FastAPI.

### Health

```http
GET /health
GET /ready
```

### Create Recovery

```http
POST /v1/recoveries
```

Example request:

```json
{
  "payment_id": "pay_001",
  "amount_inr": "4999.00",
  "recovery_probability": 0.91,
  "attempt_number": 1
}
```

Example response:

```json
{
  "payment_id": "pay_001",
  "decision": "create_payment_link",
  "execution_status": "success",
  "recovered_amount_inr": "0",
  "expected_net_value_inr": "4544.09",
  "reason": "Recovery payment link created.",
  "payment_link": "https://example.test/recover/pay_001"
}
```

### Record Recovery Outcome

```http
POST /v1/recovery-outcomes
```

Example request:

```json
{
  "payment_id": "pay_001",
  "status": "paid",
  "recovered_amount_inr": "4999.00",
  "reason": "Customer completed recovery payment."
}
```

### Recovery Metrics

```http
GET /v1/recovery-metrics
```

Example response:

```json
{
  "attempted_count": 1,
  "successful_recovery_count": 1,
  "failed_recovery_count": 0,
  "recovered_revenue_inr": "4999.00",
  "recovery_rate": 1.0
}
```

## Tech Stack

| Area | Tools |
| --- | --- |
| Language | Python 3.13 |
| API | FastAPI, Uvicorn, Pydantic |
| ML | scikit-learn, pandas, NumPy, joblib |
| MLOps | DVC, `params.yaml`, tracked metrics, reproducible model artifact |
| Package and runtime | uv, `uv.lock`, uv-based Docker build |
| Payments integration | Razorpay SDK, payment-link provider abstraction |
| State | SQLite durable store |
| Quality gates | pytest, MyPy strict mode, Ruff, pre-commit |
| Deployment | Docker, docker-compose |

## Repository Structure

```text
src/recoverai/
  agent/          Recovery decision orchestration
  api/            FastAPI app, routes, settings, dependencies
  data/           Synthetic payment dataset generation and validation
  domain/         Payment and recovery domain types
  metrics/        Recovery metrics calculation
  ml/             Feature engineering, splitting, training, evaluation
  recovery/       Executor, policy, gateway, Razorpay provider, outcomes
  service/        Application service and API schemas
  state/          Durable SQLite state store

scripts/
  generate_data.py
  train_baseline.py
  container_smoke_test.py

tests/
  unit/
  integration/

metrics/
  baseline.json

dvc.yaml
params.yaml
pyproject.toml
uv.lock
Dockerfile
```

## Run Locally

Install dependencies:

```bash
uv sync
```

Run tests:

```bash
uv run pytest -q
```

Run quality checks:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pre-commit run --all-files
```

Reproduce the ML pipeline:

```bash
uv run dvc repro
uv run dvc status
```

Start the API:

```bash
uv run uvicorn recoverai.api.app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Razorpay Test Mode

Set credentials to use the Razorpay-backed payment-link provider:

```bash
RAZORPAY_KEY_ID=<test_key_id>
RAZORPAY_KEY_SECRET=<test_key_secret>
```

Without credentials, RecoverAI uses the deterministic fake provider. This keeps local development and CI reliable while preserving a clean boundary for Razorpay Test Mode.

## Docker

Build:

```bash
docker build -t recoverai .
```

Run:

```bash
docker run -p 8000:8000 recoverai
```

## Testing Strategy

The test suite covers:

- payment domain validation
- recovery domain behavior
- agent orchestration
- executor safety limits
- payment-link provider behavior
- Razorpay provider contract
- durable recovery state
- recovery outcome recording
- recovery metrics
- API integration
- dataset quality
- ML pipeline behavior

These tests are intentionally business-facing. They check not just whether code runs, but whether the system preserves the money semantics: creating a payment link is not recovered revenue, duplicate recovery requests are skipped, and only paid outcomes increase recovered revenue.

## Highlight To A Recruiter

- I did not build a generic chatbot. I built a bounded AI workflow for a real payments problem.
- I separated decision, execution, and outcome so the system can be trusted around money movement.
- I used MLOps practices with DVC, parameterized training, tracked metrics, and reproducible model artifacts.
- I used uv, strict MyPy, Ruff, pre-commit, pytest, Docker, and typed FastAPI to show production engineering discipline.
- I integrated Razorpay through a provider abstraction so local tests stay deterministic and Razorpay Test Mode can be enabled by configuration.
- I treated idempotency and durable state as first-class requirements, not afterthoughts.
- I measured business impact in recovered rupees, not only model accuracy.

## Future Improvements

- Add Razorpay webhook ingestion for automatic outcome observation.
- Add merchant-specific policy configuration.
- Add action cooldown windows and customer opt-out enforcement.
- Add model monitoring for threshold drift and recovery-rate changes.
- Add richer recovery actions such as resend link, wait, escalate to human, and retry payment link.
- Add dashboard views for recovered revenue, failed interventions, and pending recovery links.
