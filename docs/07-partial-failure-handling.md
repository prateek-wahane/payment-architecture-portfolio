# Partial Failure Handling

## Business problem

Payment succeeds, but another service goes down during the transaction.

Example:

```text
Payment service receives success from PSP.
Order service is unavailable.
Customer payment succeeds but order is not confirmed.
```

## Root cause

The system depends synchronously on downstream services in the payment completion path.

## Solution: durable event-driven completion

```text
1. Payment service records SUCCESS.
2. Payment service posts ledger entry.
3. Payment service writes PaymentSucceeded event to outbox.
4. Event publisher publishes to broker.
5. Order service consumes event when available.
6. Order service updates order idempotently.
```

## Transactional outbox

Business state and event are written in the same database transaction.

```text
BEGIN
  update payment_order set status='SUCCESS'
  insert ledger_entry
  insert outbox_event PaymentSucceeded
COMMIT
```

## Fallback

```text
Payment remains SUCCESS.
Order remains PAYMENT_CONFIRMATION_PENDING.
Outbox retries event publishing.
Repair job compares successful payments against unpaid orders.
Ops alert triggers if mismatch exceeds threshold.
```

## Tradeoff

Async event-driven design introduces eventual consistency but prevents payment success from being lost when downstream services are unavailable.
