from collections.abc import Generator
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from recoverai.api.app import app
from recoverai.api.dependencies import get_recovery_service, get_settings


@pytest.fixture
def client(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient]:
    database_path = tmp_path / "recovery.db"

    monkeypatch.setenv(
        "RECOVERAI_STATE_DATABASE_PATH",
        str(database_path),
    )

    get_settings.cache_clear()
    get_recovery_service.cache_clear()

    with TestClient(app) as test_client:
        yield test_client

    get_recovery_service.cache_clear()
    get_settings.cache_clear()


def test_health_check(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_check(client: TestClient) -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_recovery_endpoint_executes_recovery(client: TestClient) -> None:
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
    assert body["decision"] == "create_payment_link"
    assert body["execution_status"] == "success"
    assert Decimal(body["recovered_amount_inr"]) == Decimal("1500.00")


def test_recovery_endpoint_rejects_invalid_probability(
    client: TestClient,
) -> None:
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


def test_recovery_endpoint_rejects_unknown_fields(
    client: TestClient,
) -> None:
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


def test_recovery_endpoint_handles_below_threshold(
    client: TestClient,
) -> None:
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


def test_recovery_endpoint_is_idempotent(
    client: TestClient,
) -> None:
    payload = {
        "payment_id": "pay_api_idempotent_001",
        "amount_inr": "1500.00",
        "recovery_probability": 0.95,
        "attempt_number": 1,
    }

    first_response = client.post(
        "/v1/recoveries",
        json=payload,
    )

    second_response = client.post(
        "/v1/recoveries",
        json=payload,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_body = first_response.json()
    second_body = second_response.json()

    assert first_body["execution_status"] == "success"
    assert second_body["execution_status"] == "skipped"
    assert second_body["recovered_amount_inr"] == "0"
