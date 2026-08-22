from __future__ import annotations

from enum import StrEnum


class RecoveryActionType(StrEnum):
    NO_ACTION = "no_action"
    CREATE_PAYMENT_LINK = "create_payment_link"
