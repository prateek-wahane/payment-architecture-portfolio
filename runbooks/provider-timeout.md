# Runbook: Provider Timeout

## Symptom

Payments stuck in UNKNOWN/PENDING state.

## Immediate action

1. Check provider timeout dashboard.
2. Enable circuit breaker if threshold breached.
3. Route traffic to alternate PSP.
4. Run status enquiry for stuck transactions.
5. Notify customer using pending state message.

## Do not

```text
Do not mark timeout as failed immediately.
Do not ask customer to pay again without status enquiry.
```

## Permanent fix

```text
Timeout budget
Circuit breaker
Retry with backoff and jitter
Status enquiry job
Provider health scoring
```
