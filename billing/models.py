from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    order_id: str
    amount_cents: int
    currency: str = "USD"


@dataclass(frozen=True)
class RefundRecord:
    refund_id: str
    order_id: str
    amount_cents: int
    idempotency_key: str
    replayed: bool = False
