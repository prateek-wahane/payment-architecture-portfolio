# Reconciliation and Settlement

## Business problem

Internal system says payment is successful, but PSP settlement report or bank statement does not match.

## Business impact

Finance cannot close settlement. Merchant payout may be delayed. Manual operations increase.

## Three-way reconciliation

```text
1. Internal ledger
2. PSP settlement report
3. Bank account statement
```

## Reconciliation keys

```text
provider_txn_id
payment_id
order_id
amount
currency
settlement_date
merchant_id
bank_reference
```

## Mismatch categories

```text
Internal success, PSP missing
PSP success, internal failed
Amount mismatch
Duplicate settlement
Refund missing
Chargeback received
Settlement delayed
Fee mismatch
Tax mismatch
```

## Reconciliation flow

```text
1. Import PSP report.
2. Import bank statement.
3. Match against internal ledger.
4. Auto-clear exact matches.
5. Create exception for mismatch.
6. Route exception to maker-checker workflow.
7. Post adjustment/reversal only through audited workflow.
```

## Settlement flow

```text
1. Select captured/successful payments eligible for settlement.
2. Group by merchant and settlement date.
3. Calculate gross amount.
4. Deduct fees/taxes.
5. Generate settlement batch.
6. Send payout instruction.
7. Reconcile bank confirmation.
```

## Production rule

Do not delete or mutate financial records to fix reconciliation. Use reversal or adjustment entries with audit trail.
