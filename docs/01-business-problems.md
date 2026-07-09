# Business Problems for Production Payment Architecture

This document lists production-grade payment problems in a business-first format. Each problem can be used as an interview scenario or as a case study in this repository.

---

## 1. Million-user scale problem

### Problem Statement

The payment platform slows down during peak sale traffic because payment initiation, provider call, fraud check, ledger update, notification, and order update are all executed synchronously.

### Business Statement

Customers abandon checkout because the payment page is slow or stuck. Revenue drops during high-value sale windows. Leadership loses trust in the platform's ability to handle campaigns and festival traffic.

### Production Symptom

```text
P95 payment initiation latency increased from 250 ms to 2.5 seconds.
PSP timeout rate increased from 0.3% to 4%.
Checkout abandonment increased by 12%.
```

### Required Solution

Introduce a payment orchestrator, reduce synchronous path, move non-critical work to async processing, use queue-based retries, provider routing, rate limits, and database partitioning.

---

## 2. Simultaneous transaction problem

### Problem Statement

Multiple payment requests are generated for the same order because the customer double-clicks, the mobile app retries, and the browser refreshes the payment page.

### Business Statement

Customers may be charged twice. Support tickets increase. Refund operations increase. Customer trust is damaged.

### Required Solution

Use idempotency keys, unique order constraints, request hash validation, payment attempt state machine, and provider transaction deduplication.

---

## 3. Near-zero latency problem

### Problem Statement

Customers expect immediate payment feedback, but backend payment confirmation is slow due to provider latency and synchronous dependency chains.

### Business Statement

Customers repeatedly click Pay Now or abandon checkout. The platform appears unreliable even when money movement eventually succeeds.

### Required Solution

Design for near-zero perceived latency, not impossible zero latency. Return payment intent quickly, show pending state, complete financial flow through webhook, status polling, and reconciliation.

---

## 4. Duplicate event problem

### Problem Statement

PSP sends the same payment success webhook multiple times. The system processes all events and creates duplicate ledger entries.

### Business Statement

Settlement reports become incorrect. Finance teams lose confidence in automated reports. Manual reconciliation workload increases.

### Required Solution

Persist raw webhook first, verify signature, deduplicate using provider event ID and provider transaction ID, and protect ledger writes using unique financial constraints.

---

## 5. Partial service failure problem

### Problem Statement

Payment succeeds at the provider, but the order service is unavailable. Payment is successful, but the order remains unpaid.

### Business Statement

The customer says money was deducted but the order is not confirmed. This is one of the most damaging payment incidents from a customer trust perspective.

### Required Solution

Use transactional outbox, durable PaymentSucceeded event, idempotent order consumer, retry queue, repair job, and operational alert.

---

## 6. Out-of-order event problem

### Problem Statement

PaymentSucceeded event reaches downstream before PaymentInitiated event. The downstream consumer rejects or misses the success event because the payment record is not yet present.

### Business Statement

Customer payment updates are missed. Orders remain unpaid despite successful payment. Support tickets increase.

### Required Solution

Use event versioning, state-machine dominance, buffering, replay, source-of-truth lookup, and idempotent upsert.

---

## 7. Observability problem

### Problem Statement

Support cannot trace the exact payment failure point because logs, traces, metrics, and business IDs are not correlated.

### Business Statement

Mean time to resolution increases. Customer support depends on engineering for every payment complaint. Finance closure is delayed.

### Required Solution

Use correlation ID, payment ID, order ID, provider transaction ID, trace ID, structured logs, distributed tracing, business metrics, and runbooks.

---

## 8. Reconciliation problem

### Problem Statement

Internal ledger shows success, but PSP settlement report does not match.

### Business Statement

Finance cannot close settlement accurately. Manual investigation is required. Merchant payout may be delayed.

### Required Solution

Implement three-way reconciliation between internal ledger, PSP report, and bank statement.

---

## 9. Provider outage problem

### Problem Statement

One PSP is failing, but traffic continues to be routed to it.

### Business Statement

Payment success rate drops. Customers cannot complete checkout. Business loses revenue.

### Required Solution

Use provider health scoring, circuit breaker, dynamic routing, rate limits, and fallback PSPs.

---

## 10. Stuck payment problem

### Problem Statement

Payments remain in UNKNOWN state because webhooks were delayed or lost.

### Business Statement

Customers do not know whether payment succeeded. Orders remain pending. Support volume increases.

### Required Solution

Use status enquiry, payment repair jobs, reconciliation exception workflow, and customer notification.
