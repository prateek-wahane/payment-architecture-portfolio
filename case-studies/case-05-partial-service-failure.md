# Case 05: Partial Service Failure During Payment

## Business Problem Statement

Payment succeeds but order service is down, leaving order unpaid.

## Business Impact

Customer money is deducted but order is not confirmed. This severely damages trust.

## Technical Problem Statement

Payment completion depends synchronously on order service.

## Production Failure Scenario

```text
PSP confirms success
Webhook arrives
Payment service calls Order Service
Order Service is down
Order remains unpaid
```

## Solution

Use transactional outbox and durable PaymentSucceeded event. Order service consumes idempotently when available.

## Production Controls

```text
Outbox table
Message broker retry
Idempotent order update
Repair job
DLQ
```

## Fallback

```text
Payment SUCCESS
Order PAYMENT_CONFIRMATION_PENDING
Retry event
Run repair job
Alert ops
```

## Observability

```text
payment_success_order_unpaid_count
outbox_unpublished_count
consumer_lag
DLQ count
```

## Tradeoffs

```text
Event-driven design improves resilience but introduces eventual consistency.
```

## Revisit Criteria

```text
Mismatch count exceeds threshold
Order consumer lag increases
Repair job volume increases
```

## Interview Explanation

> A downstream outage must not cause loss of payment success. I persist financial truth first, then propagate events durably.
