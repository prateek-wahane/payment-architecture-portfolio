# Case 07: Production Remediation and Self-Healing

## Business Problem Statement

Payments remain stuck in UNKNOWN because provider webhook was delayed or lost.

## Business Impact

Customers do not know whether payment succeeded. Orders remain pending. Support load increases.

## Technical Problem Statement

The platform lacks automated repair for stuck payment states.

## Production Failure Scenario

```text
Payment initiated
Provider processes payment
Webhook lost
Internal status remains UNKNOWN
Customer contacts support
```

## Solution

Build payment repair job that queries provider status and updates internal state safely.

## Production Controls

```text
Scheduled repair job
Provider status enquiry
Idempotent state update
Ledger backfill
Outbox event replay
Maker-checker manual correction
```

## Fallback

```text
Manual operations workflow
Finance approval
Customer notification after confirmed status
```

## Observability

```text
unknown_payment_age
repair_success_count
repair_failure_count
manual_repair_count
provider_status_enquiry_error
```

## Tradeoffs

```text
Automated repair reduces MTTR but must avoid incorrect state correction from stale provider data.
```

## Revisit Criteria

```text
Stuck payment count grows
Repair failure rate increases
Manual repair volume increases
```

## Interview Explanation

> Production-grade payment systems need self-healing for stuck states, missing webhooks, and unpublished events.
