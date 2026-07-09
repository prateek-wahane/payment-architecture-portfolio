# Idempotency and Duplicate Handling

## Problem

In payment systems, duplicates are normal.

They happen because of:

```text
customer double-click
mobile retry
browser refresh
load balancer retry
client timeout
PSP duplicate webhook
message broker redelivery
manual replay
```

## Design

Every payment request must include an idempotency key.

```text
merchant_id + idempotency_key = unique request identity
merchant_id + order_id = unique active payment order
provider + provider_txn_id = unique provider transaction
provider + provider_event_id = unique webhook event
```

## Algorithm

```text
1. Receive payment request.
2. Validate idempotency key.
3. Generate request hash.
4. Check idempotency_record.
5. If key exists and hash matches, return stored response.
6. If key exists and hash differs, reject as conflict.
7. If key does not exist, insert PROCESSING record.
8. Create payment order and attempt in one transaction.
9. Store response against idempotency key.
```

## Duplicate webhook handling

```text
1. Verify signature.
2. Store raw event.
3. Deduplicate using provider_event_id.
4. Deduplicate business effect using provider_txn_id and event_type.
5. Apply state transition only if valid.
6. Return HTTP 200 for already processed duplicate events.
```

## Anti-patterns

```text
Relying only on frontend disabling the Pay button.
Treating timeout as failure.
Creating a new payment attempt for every retry.
Updating ledger without unique transaction constraint.
Allowing SUCCESS to move backward to PENDING.
```

## Production-ready answer

> I design duplicate handling at multiple layers: API idempotency, database uniqueness, provider transaction uniqueness, webhook deduplication, state-machine transition control, and append-only ledger constraints. The goal is that the same financial event can be replayed multiple times but creates financial impact only once.
