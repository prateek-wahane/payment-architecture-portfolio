# Case 06: Observability and Debugging

## Business Problem Statement

Support cannot quickly resolve 'money deducted but order not confirmed' complaints.

## Business Impact

MTTR increases, customers wait longer, and support depends on engineering.

## Technical Problem Statement

Logs, traces, events, and database rows are not correlated.

## Production Failure Scenario

```text
Customer shares order_id
Support checks order system only
Payment data is in another service
Provider_txn_id missing
Engineering manually queries databases
```

## Solution

Introduce end-to-end correlation IDs, structured logs, traces, business metrics, and runbooks.

## Production Controls

```text
correlation_id everywhere
payment_id/order_id/provider_txn_id in logs
trace propagation
business dashboards
alert rules
```

## Fallback

```text
Use manual database correlation
Run reconciliation query
Trigger repair job
Escalate to provider if needed
```

## Observability

```text
correlation_id coverage
MTTR
unknown_payment_count
payment_success_order_unpaid_count
reconciliation_exception_count
```

## Tradeoffs

```text
Detailed logging improves diagnosis but increases storage cost and requires masking sensitive data.
```

## Revisit Criteria

```text
MTTR > 30 minutes
Support cannot self-serve transaction status
Correlation ID missing
```

## Interview Explanation

> Observability must answer where the customer's money is, not just whether servers are up.
