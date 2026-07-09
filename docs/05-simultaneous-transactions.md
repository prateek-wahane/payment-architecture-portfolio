# Simultaneous Transactions

## Business problem

A customer starts multiple payment flows for the same order through browser retries, mobile retry, or double-click behavior.

## Technical problem

The backend allows more than one active payment attempt for the same order.

## Failure timeline

```text
T1: Customer clicks Pay Now.
T2: Payment API call times out at frontend.
T3: Customer clicks again.
T4: Backend creates second payment attempt.
T5: Both attempts reach PSP.
T6: PSP confirms both.
T7: Customer is charged twice.
```

## Solution

Use order-level payment locking and attempt lifecycle rules.

```text
Only one active attempt can exist per order.
A new attempt is allowed only if previous attempt is terminal.
```

Terminal states:

```text
FAILED
EXPIRED
CANCELLED
```

Non-terminal states:

```text
CREATED
INITIATED
PENDING
AUTHORIZED
SUCCESS
UNKNOWN
```

## Implementation

```sql
CREATE UNIQUE INDEX uq_payment_order_active
ON payment_order(merchant_id, order_id);
```

For advanced retry:

```text
payment_order has one logical payment.
payment_attempt can have multiple rows.
Only one payment_attempt can be ACTIVE at a time.
```

## Tradeoff

Strict locking prevents duplicate charges but can block legitimate retries when an attempt is stuck.  
The remedy is to use a clear expiry/timeout policy and provider status enquiry before allowing another attempt.
