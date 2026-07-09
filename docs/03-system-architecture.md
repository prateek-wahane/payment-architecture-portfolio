# System Architecture

## High-level architecture

```plantuml
@startuml
skinparam componentStyle rectangle

actor Customer
component "Ecommerce App" as App
component "API Gateway / WAF" as Gateway
component "Payment Orchestrator" as Pay
component "Idempotency Service" as Idem
component "Risk Service" as Risk
component "Provider Routing Engine" as Route
component "PSP Adapter" as Adapter
component "External PSP / Bank" as PSP
database "Payment OLTP DB" as DB
database "Ledger DB" as Ledger
queue "Message Broker" as MQ
component "Webhook Processor" as Webhook
component "Order Service" as Order
component "Reconciliation Engine" as Recon
component "Settlement Service" as Settle
component "Observability Stack" as Obs

Customer --> App
App --> Gateway
Gateway --> Pay
Pay --> Idem
Pay --> Risk
Pay --> Route
Route --> Adapter
Adapter --> PSP
PSP --> Webhook
Pay --> DB
Pay --> Ledger
Pay --> MQ
Webhook --> DB
Webhook --> MQ
MQ --> Order
MQ --> Recon
MQ --> Settle
Pay --> Obs
Webhook --> Obs
Order --> Obs
Recon --> Obs
@enduml
```

## Critical synchronous path

```text
Request validation
Idempotency check
Payment intent creation
Provider initiation
Immediate response to user
```

## Async path

```text
Webhook processing
Ledger posting
Order confirmation
Notification
Reconciliation
Settlement
Analytics
```

## Component responsibilities

### Payment Orchestrator

Owns payment lifecycle, state machine, idempotency, provider routing, and event emission.

### PSP Adapter

Isolates provider-specific API contracts, authentication, signing, status mapping, and retries.

### Webhook Processor

Receives external provider events, validates signature, persists raw event, deduplicates, and triggers state transition.

### Ledger Service

Maintains append-only financial entries. No deletes. Corrections are reversals.

### Reconciliation Engine

Compares internal ledger, PSP settlement report, and bank statement.

### Settlement Service

Groups settled transactions, calculates fees/taxes, and generates merchant payout batches.

### Observability Stack

Captures metrics, logs, traces, business events, and alerts.

## Architecture decision

Customer-facing flow can be fast, but financial completion must be durable and correct.
