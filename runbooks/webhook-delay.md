# Runbook: Webhook Delay

## Symptom

Provider confirms payment but webhook is delayed.

## Immediate action

1. Check webhook receive rate.
2. Check provider status page/contact.
3. Run status enquiry for old pending payments.
4. Monitor webhook processing lag.
5. Reconcile once provider report arrives.

## Metrics

```text
webhook_delay_seconds
webhook_received_count
webhook_processing_error_count
unknown_payment_age
```
