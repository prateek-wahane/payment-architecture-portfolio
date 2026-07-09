# Observability and Debugging

## Business problem

Customer reports: "Money deducted, order not confirmed."

Engineering needs to answer:

```text
Did payment initiate?
Did provider confirm?
Did webhook arrive?
Did ledger post?
Did order update?
Did settlement reconcile?
```

## Required IDs

Every log, trace, event, and database row should carry:

```text
correlation_id
trace_id
payment_id
order_id
merchant_id
customer_id
provider
provider_txn_id
idempotency_key
event_id
settlement_batch_id
```

## Structured log example

```json
{
  "timestamp": "2026-07-09T10:15:30Z",
  "level": "INFO",
  "service": "payment-orchestrator",
  "correlation_id": "corr_123",
  "trace_id": "trace_456",
  "payment_id": "pay_789",
  "order_id": "ord_456",
  "provider": "PSP_A",
  "provider_txn_id": "psp_999",
  "event": "PAYMENT_SUCCEEDED",
  "state_from": "PENDING",
  "state_to": "SUCCESS"
}
```

## Debugging flow

```text
1. Search by order_id.
2. Find payment_id.
3. Check payment_order status.
4. Check payment_attempt provider_txn_id.
5. Check webhook_event table.
6. Check ledger_entry table.
7. Check outbox_event table.
8. Check message broker lag/DLQ.
9. Check order service consumer logs.
10. Check reconciliation status.
```

## Narrowing logic

### Payment order missing

Likely issue:

```text
API failed before DB commit.
```

Check:

```text
API gateway logs
payment service logs
DB connection errors
idempotency table
```

### Payment success but ledger missing

Likely issue:

```text
Webhook processed partially or ledger write failed.
```

Check:

```text
webhook_event
state transition logs
ledger_entry
DLQ
outbox_event
```

### Ledger exists but order unpaid

Likely issue:

```text
Order service consumer failed.
```

Check:

```text
PaymentSucceeded event
broker consumer lag
order service logs
DLQ
order update idempotency
```

### Internal success but provider missing

Likely issue:

```text
Incorrect provider status mapping or unconfirmed response.
```

Check:

```text
raw PSP response
provider status enquiry
PSP settlement file
reconciliation exception
```

## Alerts

```text
Payment unknown count > threshold
Payment success but order unpaid > threshold
Webhook delay > 5 minutes
Provider timeout rate > 2%
Outbox unpublished events > threshold
DLQ count > threshold
Reconciliation mismatch > threshold
P99 latency breach
```

## Production-ready answer

> Observability must be business-transaction oriented. Infrastructure metrics tell me the system is running. Business observability tells me where the customer’s money is.
