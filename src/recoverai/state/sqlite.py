from __future__ import annotations

import sqlite3
from decimal import Decimal

from recoverai.state.store import (
    StoredPaymentLink,
    StoredRecovery,
    StoredRecoveryOutcome,
)


class SQLiteRecoveryStateStore:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS recoveries (
                    idempotency_key TEXT PRIMARY KEY,
                    payment_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    recovered_amount_inr TEXT NOT NULL,
                    reason TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS payment_links (
                    idempotency_key TEXT PRIMARY KEY,
                    payment_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    amount_inr TEXT NOT NULL,
                    url TEXT NOT NULL,
                    reason TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS recovery_outcomes (
                    idempotency_key TEXT PRIMARY KEY,
                    payment_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    recovered_amount_inr TEXT NOT NULL,
                    reason TEXT NOT NULL
                )
                """
            )

    def get_recovery(
        self,
        idempotency_key: str,
    ) -> StoredRecovery | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    payment_id,
                    idempotency_key,
                    status,
                    recovered_amount_inr,
                    reason
                FROM recoveries
                WHERE idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()

        if row is None:
            return None

        return StoredRecovery(
            payment_id=row[0],
            idempotency_key=row[1],
            status=row[2],
            recovered_amount_inr=Decimal(row[3]),
            reason=row[4],
        )

    def save_recovery(
        self,
        recovery: StoredRecovery,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO recoveries (
                    idempotency_key,
                    payment_id,
                    status,
                    recovered_amount_inr,
                    reason
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    recovery.idempotency_key,
                    recovery.payment_id,
                    recovery.status,
                    str(recovery.recovered_amount_inr),
                    recovery.reason,
                ),
            )

    def get_payment_link(
        self,
        idempotency_key: str,
    ) -> StoredPaymentLink | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    payment_id,
                    idempotency_key,
                    status,
                    amount_inr,
                    url,
                    reason
                FROM payment_links
                WHERE idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()

        if row is None:
            return None

        return StoredPaymentLink(
            payment_id=row[0],
            idempotency_key=row[1],
            status=row[2],
            amount_inr=Decimal(row[3]),
            url=row[4],
            reason=row[5],
        )

    def save_payment_link(
        self,
        payment_link: StoredPaymentLink,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO payment_links (
                    idempotency_key,
                    payment_id,
                    status,
                    amount_inr,
                    url,
                    reason
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    payment_link.idempotency_key,
                    payment_link.payment_id,
                    payment_link.status,
                    str(payment_link.amount_inr),
                    payment_link.url,
                    payment_link.reason,
                ),
            )

    def get_recovery_outcome(
        self,
        idempotency_key: str,
    ) -> StoredRecoveryOutcome | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    payment_id,
                    idempotency_key,
                    status,
                    recovered_amount_inr,
                    reason
                FROM recovery_outcomes
                WHERE idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()

        if row is None:
            return None

        return StoredRecoveryOutcome(
            payment_id=row[0],
            idempotency_key=row[1],
            status=row[2],
            recovered_amount_inr=Decimal(row[3]),
            reason=row[4],
        )

    def save_recovery_outcome(
        self,
        outcome: StoredRecoveryOutcome,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR REPLACE INTO recovery_outcomes (
                    idempotency_key,
                    payment_id,
                    status,
                    recovered_amount_inr,
                    reason
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    outcome.idempotency_key,
                    outcome.payment_id,
                    outcome.status,
                    str(outcome.recovered_amount_inr),
                    outcome.reason,
                ),
            )

    def list_recovery_outcomes(self) -> list[StoredRecoveryOutcome]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    payment_id,
                    idempotency_key,
                    status,
                    recovered_amount_inr,
                    reason
                FROM recovery_outcomes
                ORDER BY rowid
                """
            ).fetchall()

        return [
            StoredRecoveryOutcome(
                payment_id=row[0],
                idempotency_key=row[1],
                status=row[2],
                recovered_amount_inr=Decimal(row[3]),
                reason=row[4],
            )
            for row in rows
        ]
