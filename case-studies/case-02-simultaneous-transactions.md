# Case 02: Simultaneous Transactions on Same Order

## Business Problem Statement

A customer creates multiple payment attempts for the same order due to double-clicks and frontend retries.

## Business Impact

Customer may be charged twice, creating refund cost and trust loss.

## Technical Problem Statement

The backend allows multiple active payment attempts for one order.

## Production Failure Scenario

```text
T1 customer clicks Pay
T2 frontend times out
T3 customer retries
T4 second attempt created
T5 both reach PSP
T6 both succeed
```

## Solution

Use idempotency keys, unique order constraints, active-attempt locking, and provider transaction dedupe.

## Production Controls

```text
UNIQUE(merchant_id, order_id)
UNIQUE(merchant_id, idempotency_key)
UNIQUE(provider, provider_txn_id)
State machine transition guard
```

## Fallback

```text
Freeze duplicate settlement
Keep one successful payment
Refund/reverse duplicate
Notify support/customer
```

## Observability

```text
duplicate_attempt_count
multiple_success_same_order
refund_due_to_duplicate
idempotency_conflict_count
```

## Tradeoffs

```text
Strict locking prevents duplicate charge but may block legitimate retry while previous attempt is stuck.
```

## Revisit Criteria

```text
Duplicate complaints > 0
Multiple successful attempts for same order
Manual refunds increasing
```

## Interview Explanation

> I never rely on the frontend for duplicate prevention. The backend must guarantee no duplicate financial effect.
