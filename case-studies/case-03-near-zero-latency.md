# Case 03: Near-Zero Payment Latency

## Business Problem Statement

Customers expect instant payment feedback, but checkout appears slow.

## Business Impact

Customers abandon checkout or retry payment unnecessarily.

## Technical Problem Statement

The critical request path includes fraud, PSP, ledger, notification, and order update synchronously.

## Production Failure Scenario

```text
Payment API waits for 5 downstream operations
Provider latency spikes
Customer sees spinner
Customer retries
```

## Solution

Minimize synchronous path and move completion to durable async flow.

## Production Controls

```text
Fast payment intent
Async webhook processing
Status polling
Pending-first UX
Timeout budget
```

## Fallback

```text
Show confirmation pending
Disable repeated Pay button
Run status enquiry
Notify after final status
```

## Observability

```text
payment_intent_latency
provider_latency
pending_state_age
status_poll_count
abandonment_rate
```

## Tradeoffs

```text
Pending-first UX is safer but needs clear customer communication.
```

## Revisit Criteria

```text
Payment page abandonment increases
Pending payments exceed SLA
Customer complaints increase
```

## Interview Explanation

> Zero latency is not real. I design for near-zero perceived latency while preserving financial correctness.
