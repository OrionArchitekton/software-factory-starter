import pytest

from billing.models import Order
from billing.refunds import RefundService


def make_service() -> RefundService:
    return RefundService(
        orders={
            "ord_101": Order(order_id="ord_101", amount_cents=10000),
            "ord_102": Order(order_id="ord_102", amount_cents=2500),
        }
    )


def test_order_store_starts_empty() -> None:
    svc = make_service()
    assert svc.refunded_total("ord_101") == 0
