# Case 01: Million User Payment Scale

## Business Problem Statement

During sale traffic, checkout payment initiation slows down and customers abandon payment.

## Business Impact

Revenue drops during peak business hours. Customer confidence in checkout reliability decreases.

## Technical Problem Statement

The system was designed for average TPS. It performs too many synchronous operations and lacks backpressure.

## Production Failure Scenario

```text
Normal: 300 TPS
Peak: 3,000 TPS
Retry amplification: 1,500 TPS
Effective load: 4,500+ TPS
```

## Solution

Introduce payment orchestrator, async completion, horizontal scaling, queue-based retry, provider routing, and DB partitioning.

## Production Controls

```text
API rate limits
Circuit breaker
Queue backpressure
Connection pool limits
Partitioned OLTP tables
Provider health scoring
```

## Fallback

```text
Mark payment PENDING/UNKNOWN during provider slowdown
Route to alternate provider
Run status enquiry
Reconcile later
```

## Observability

```text
P95/P99 latency
Provider timeout rate
Queue lag
Unknown payment count
Checkout abandonment
DB CPU and lock wait
```

## Tradeoffs

```text
Async completion improves resilience but introduces eventual consistency.
Synchronous completion is simpler but fragile under latency.
```

## Revisit Criteria

```text
P99 > 1s
Unknown payments > 1%
Queue lag > 2 minutes
Provider timeout > 2%
```

## Interview Explanation

> At 1M+ user scale, I design for peak, retries, and provider instability, not just average throughput.
