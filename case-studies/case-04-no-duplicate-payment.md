# Case 04: No Duplicate Financial Effect

## Business Problem Statement

Duplicate PSP webhooks create duplicate payment success processing.

## Business Impact

Ledger and settlement become unreliable. Finance must manually fix reports.

## Technical Problem Statement

Webhook consumer is not idempotent and re-applies the same financial event.

## Production Failure Scenario

```text
Webhook success arrives
Ledger entry created
Provider retries same webhook
Ledger entry created again
```

## Solution

Persist webhook, deduplicate event, apply state transition once, protect ledger with unique constraints.

## Production Controls

```text
UNIQUE(provider, provider_event_id)
UNIQUE(transaction_id, account_id, entry_type, event_type)
Idempotent webhook consumer
State dominance rules
```

## Fallback

```text
Stop settlement batch
Create reversal entries
Re-run reconciliation
Alert on duplicate financial effect
```

## Observability

```text
duplicate_webhook_count
ledger_duplicate_reject_count
reversal_count
reconciliation_mismatch
```

## Tradeoffs

```text
Provider-event dedupe is simple but may not catch duplicate business events with different event IDs.
```

## Revisit Criteria

```text
Duplicate provider behavior changes
Reconciliation mismatch caused by duplicate events
```

## Interview Explanation

> Duplicate delivery is expected. The system must be at-least-once tolerant and effectively-once at business level.
