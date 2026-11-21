# Task: Safe Partial Refunds with Idempotency

## Goal
Implement `process_refund(order_id, amount_cents, idempotency_key)` in `billing/refunds.py`.

## Acceptance Criteria
1. Reject any refund where `amount_cents <= 0` with `ValueError`.
2. Reject any refund for an unknown `order_id` with `KeyError`.
3. Never allow total refunded amount for an order to exceed the original charge (`order.amount_cents`), including across multiple partial refunds.
4. If the same `idempotency_key` is submitted again for the same order, return the original `RefundRecord` without charging or deducting a second time.
5. Keep `main` untouched. Do all work in an isolated git worktree and pass `./check.sh` before reporting done.

## Out of Scope
- External payment gateway HTTP calls
- Currency conversion
