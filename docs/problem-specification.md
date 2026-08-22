# RecoverAI Problem Specification

## Track

Track 03: AI Revenue Recovery

## Problem

RecoverAI identifies failed payment attempts that represent recoverable revenue,
determines the likely cause, selects a bounded recovery intervention, and tracks
whether the intervention successfully recovered the payment.

## Initial Scope

The first implementation focuses on failed payment recovery.

The system will initially operate on synthetic payment-event data.

Razorpay Test Mode integration will be introduced only after the local recovery
workflow, policy engine, evaluation framework, and audit trail are working.

## Core Workflow

1. Ingest payment event.
2. Validate event.
3. Generate recovery features.
4. Estimate probability of recovery.
5. Determine failure category.
6. Evaluate recovery policy.
7. Select an allowed intervention.
8. Execute or simulate the intervention.
9. Record the outcome.
10. Calculate recovered revenue.
11. Write an audit event.

## Recovery Actions

The initial action vocabulary is:

- NO_ACTION
- RETRY_PAYMENT
- SEND_PAYMENT_LINK
- SEND_REMINDER
- OFFER_ALTERNATIVE_METHOD
- ESCALATE_TO_HUMAN

The system must never dynamically invent a financial action.

## Safety Boundaries

- No live payment actions.
- No live credentials.
- No uncapped retries.
- No action outside the approved action vocabulary.
- Every action requires deterministic policy approval.
- High-value or ambiguous cases require human escalation.
- Every action must generate an audit record.
- Recovery workflows must have explicit stopping conditions.

## Machine Learning Objective

Estimate:

`P(payment is recoverable | payment context)`

The model output is advisory.

The model does not directly execute financial actions.

## Business Objective

Maximize recovered revenue while minimizing:

- unnecessary interventions
- repeated retries
- false-positive recovery attempts
- customer friction
- operational escalation

## Evaluation

### Model Metrics

- Precision
- Recall
- F1
- ROC-AUC
- PR-AUC
- Calibration

### Business Metrics

- At-risk revenue
- Eligible revenue
- Recovered revenue
- Recovery rate
- Recovery uplift
- Revenue per intervention
- False-positive cost
- Unnecessary retry count

## Initial Success Criterion

The system must process a held-out synthetic batch and report:

1. model performance,
2. recovery decisions,
3. policy-blocked actions,
4. recovered revenue,
5. unrecovered revenue,
6. complete audit trail.

No single example will be treated as evidence of system performance.