from enum import StrEnum


class PaymentMethod(StrEnum):
    CARD = "card"
    UPI = "upi"
    NETBANKING = "netbanking"
    WALLET = "wallet"


class FailureCategory(StrEnum):
    TRANSIENT = "transient"
    CUSTOMER_ACTION_REQUIRED = "customer_action_required"
    PAYMENT_METHOD = "payment_method"
    RISK_REVIEW = "risk_review"
    UNKNOWN = "unknown"


class RecoveryAction(StrEnum):
    NO_ACTION = "no_action"
    RETRY_PAYMENT = "retry_payment"
    SEND_PAYMENT_LINK = "send_payment_link"
    SEND_REMINDER = "send_reminder"
    OFFER_ALTERNATIVE_METHOD = "offer_alternative_method"
    ESCALATE_TO_HUMAN = "escalate_to_human"
