# Runbook: Reconciliation Mismatch

## Symptom

Internal ledger, PSP report, and bank statement do not match.

## Immediate action

1. Identify mismatch type.
2. Pause merchant settlement if financial risk exists.
3. Compare internal ledger, PSP report, and bank statement.
4. Create exception record.
5. Resolve through maker-checker workflow.

## Do not

```text
Do not delete ledger rows.
Do not manually update financial state without audit.
```

## Permanent fix

```text
Three-way reconciliation
Automated exception classification
Ledger reversal flow
Provider report validation
```
