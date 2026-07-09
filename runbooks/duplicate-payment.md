# Runbook: Duplicate Payment

## Symptom

Customer reports two debits for one order.

## Immediate action

1. Search by order_id.
2. Identify payment_id and provider_txn_id.
3. Check if multiple SUCCESS attempts exist.
4. Freeze impacted settlement if not paid out.
5. Mark duplicate for refund/reversal.
6. Notify support.

## Queries

```sql
SELECT * FROM payment_order WHERE order_id = :order_id;
SELECT * FROM payment_attempt WHERE payment_order_id = :payment_order_id;
SELECT * FROM ledger_entry WHERE transaction_id = :payment_id;
```

## Root-cause checks

```text
Idempotency key missing
Duplicate frontend retry
Webhook duplicate
Provider transaction duplicated
State transition allowed duplicate success
```

## Permanent fix

```text
Unique constraints
Idempotency enforcement
Webhook dedupe
Ledger uniqueness
State machine transition guard
```
