# Production Runbooks Index

Use these runbooks during incidents.

## Runbooks

| Incident | Runbook |
|---|---|
| Duplicate payment | `runbooks/duplicate-payment.md` |
| Provider timeout | `runbooks/provider-timeout.md` |
| Webhook delay | `runbooks/webhook-delay.md` |
| Reconciliation mismatch | `runbooks/reconciliation-mismatch.md` |
| Queue lag | `runbooks/queue-lag.md` |
| Partial service outage | `runbooks/partial-service-outage.md` |

## Severity guide

### SEV-1

```text
Large number of customers charged but orders not confirmed.
Payment success rate drops severely.
Settlement data corrupted.
Duplicate charges confirmed.
```

### SEV-2

```text
Single provider outage with fallback available.
Webhook delay affecting payment confirmation.
Reconciliation mismatch above threshold.
```

### SEV-3

```text
Minor delay in status update.
Small number of stuck payments.
Non-critical dashboard issue.
```

## Incident communication template

```text
Impact:
Start time:
Affected provider/service:
Affected transaction count:
Customer-visible symptom:
Current mitigation:
Next update:
Owner:
```
