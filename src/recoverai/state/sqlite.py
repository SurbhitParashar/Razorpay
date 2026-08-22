from __future__ import annotations

import sqlite3
from decimal import Decimal

from recoverai.state.store import StoredRecovery


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
