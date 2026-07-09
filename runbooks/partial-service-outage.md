# Runbook: Partial Service Outage During Payment

## Symptom

Payment succeeds but order is not confirmed.

## Immediate action

1. Confirm payment status in payment_order.
2. Check ledger entry.
3. Check outbox_event for PaymentSucceeded.
4. Check broker/DLQ.
5. Check order service consumer logs.
6. Re-publish or replay event if safe.
7. Run repair job for stuck orders.

## Permanent fix

```text
Transactional outbox
Idempotent consumers
Repair job
Business alert: payment_success_order_unpaid_count
```
