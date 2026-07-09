# Runbook: Queue Lag

## Symptom

Payment events are delayed. Order updates or reconciliation jobs lag.

## Immediate action

1. Check consumer group lag.
2. Check consumer error logs.
3. Check DLQ.
4. Scale consumers if safe.
5. Pause non-critical consumers if needed.
6. Protect database from overload.

## Root causes

```text
Poison message
Consumer deployment issue
Database slowness
Broker partition imbalance
Downstream outage
```
