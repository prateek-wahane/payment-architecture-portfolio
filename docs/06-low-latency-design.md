# Near-Zero Latency Design

## Business problem

Customers expect fast payment feedback. If the payment page takes too long, customers retry or abandon checkout.

## Architect correction

Zero latency is impossible. The realistic goal is:

```text
near-zero perceived latency
low API latency
durable asynchronous completion
fast customer status visibility
```

## Critical path budget

```text
API Gateway validation: 20 ms
Idempotency check: 30 ms
Payment intent creation: 50 ms
Risk pre-check: 50 ms
Provider initiation: 150-300 ms
```

## Design

Keep the synchronous path minimal.

```text
Synchronous:
- validate request
- check idempotency
- create payment intent
- initiate provider session
- return status/session

Asynchronous:
- webhook processing
- ledger
- order update
- notification
- reconciliation
- settlement
```

## Fallback UX

If provider is slow:

```text
Show payment pending.
Disable repeated Pay button.
Display "We are confirming your payment."
Poll payment status.
Send notification after final confirmation.
```

## Tradeoff

Immediate success improves UX but risks false confirmation.  
Pending-first design is safer but requires good customer communication.
