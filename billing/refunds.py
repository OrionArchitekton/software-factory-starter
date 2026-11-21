from billing.models import Order, RefundRecord


class RefundService:
    """In-memory refund processor used for the 3-file software factory starter."""

    def __init__(self, orders: dict[str, Order]) -> None:
        self._orders = dict(orders)
        self._refunds: list[RefundRecord] = []
        self._by_key: dict[tuple[str, str], RefundRecord] = {}

    def refunded_total(self, order_id: str) -> int:
        return sum(r.amount_cents for r in self._refunds if r.order_id == order_id)

    def process_refund(
        self, order_id: str, amount_cents: int, idempotency_key: str
    ) -> RefundRecord:
        raise NotImplementedError("Implement per task.md")
