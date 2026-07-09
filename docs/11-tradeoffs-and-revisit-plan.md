# Tradeoffs and Revisit Plan

## Sync vs async payment completion

### Chosen

Async completion after payment initiation.

### Why

Improves resilience during provider latency and downstream service failure.

### Tradeoff

Introduces eventual consistency between payment and order.

### Revisit when

```text
customer confusion increases
status page is not real-time enough
pending payment count exceeds SLA
```

---

## Kafka/event stream vs MQ

### Chosen

Use MQ-style messaging for payment commands and event streaming for business events.

### Why

Payment instructions and business events have different semantics.

### Tradeoff

Two messaging patterns increase operational complexity.

### Revisit when

```text
operational cost becomes too high
ordering issues increase
throughput requirements change
```

---

## Strict idempotency vs flexible retry

### Chosen

Strict idempotency at API and financial-effect layers.

### Why

Prevents duplicate charges.

### Tradeoff

Can block legitimate retry if first attempt is stuck.

### Revisit when

```text
unknown payment attempts increase
customer retry complaints increase
```

---

## Active-active vs active-passive

### Chosen

Active-active for stateless services; controlled failover for ledger and settlement.

### Why

Avoids split-brain financial posting.

### Tradeoff

Failover may not be instant for core financial state.

### Revisit when

```text
RTO target becomes stricter
multi-region consistency design matures
```

---

## Detailed logging vs storage cost

### Chosen

Detailed structured logs with sensitive data masking.

### Why

Payment incidents require fast root-cause analysis.

### Tradeoff

Higher log storage cost.

### Revisit when

```text
log cost exceeds budget
MTTR is already consistently low
```
