from decimal import Decimal

from fastapi.testclient import TestClient

from recoverai.api.app import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_check() -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_recovery_endpoint_executes_recovery() -> None:
    response = client.post(
        "/v1/recoveries",
        json={
            "payment_id": "pay_api_001",
            "amount_inr": "1500.00",
            "recovery_probability": 0.95,
            "attempt_number": 1,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["payment_id"] == "pay_api_001"
    assert body["decision"] == "recover"
    assert body["execution_status"] == "success"
    assert Decimal(body["recovered_amount_inr"]) == Decimal("1500.00")


def test_recovery_endpoint_rejects_invalid_probability() -> None:
    response = client.post(
        "/v1/recoveries",
        json={
            "payment_id": "pay_api_002",
            "amount_inr": "1500.00",
            "recovery_probability": 1.5,
            "attempt_number": 1,
        },
    )

    assert response.status_code == 422


def test_recovery_endpoint_rejects_unknown_fields() -> None:
    response = client.post(
        "/v1/recoveries",
        json={
            "payment_id": "pay_api_003",
            "amount_inr": "1500.00",
            "recovery_probability": 0.95,
            "attempt_number": 1,
            "unexpected": True,
        },
    )

    assert response.status_code == 422


def test_recovery_endpoint_handles_below_threshold() -> None:
    response = client.post(
        "/v1/recoveries",
        json={
            "payment_id": "pay_api_004",
            "amount_inr": "1500.00",
            "recovery_probability": 0.2,
            "attempt_number": 1,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["decision"] == "no_action"
    assert body["execution_status"] == "skipped"
