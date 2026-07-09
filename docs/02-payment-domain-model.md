# Payment Domain Model

## Core entities

```text
PaymentOrder
PaymentAttempt
WebhookEvent
LedgerEntry
OutboxEvent
ReconciliationItem
SettlementBatch
Refund
Dispute
```

## PaymentOrder

Represents the business-level payment for an ecommerce order.

Important fields:

```text
payment_order_id
merchant_id
order_id
customer_id
amount
currency
status
idempotency_key
created_at
updated_at
version
```

## PaymentAttempt

Represents one attempt to complete a payment through a provider.

```text
payment_attempt_id
payment_order_id
provider
provider_txn_id
payment_method
status
request_hash
error_code
created_at
updated_at
```

## WebhookEvent

Stores provider callback events durably before processing.

```text
provider
provider_event_id
provider_txn_id
event_type
raw_payload
signature_valid
processed_status
received_at
```

## LedgerEntry

Append-only record of financial movement.

```text
transaction_id
account_id
entry_type: DEBIT/CREDIT
amount
currency
event_type
created_at
```

Invariant:

```text
For every financial transaction:
SUM(debits) = SUM(credits)
```

## State dominance rules

```text
FAILED cannot override SUCCESS.
PENDING cannot override SUCCESS.
INITIATED cannot override CAPTURED.
CAPTURED cannot override SETTLED.
Refund and chargeback are separate financial events.
```

## Payment states

```text
CREATED
INITIATED
PENDING
AUTHORIZED
SUCCESS
FAILED
UNKNOWN
SETTLEMENT_PENDING
SETTLED
REFUND_PENDING
REFUNDED
DISPUTED
CHARGEBACK
```

## Why UNKNOWN is important

Timeout is not failure. UNKNOWN means the local system does not know the final state.  
The system must resolve UNKNOWN using webhook, provider status enquiry, or reconciliation.
