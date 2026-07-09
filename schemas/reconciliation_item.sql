CREATE TABLE reconciliation_item (
  id BIGINT PRIMARY KEY,
  payment_id VARCHAR(128) NOT NULL,
  provider VARCHAR(64) NOT NULL,
  provider_txn_id VARCHAR(128),
  internal_amount_minor BIGINT,
  provider_amount_minor BIGINT,
  bank_amount_minor BIGINT,
  currency CHAR(3) NOT NULL,
  mismatch_type VARCHAR(64),
  status VARCHAR(32) NOT NULL,
  settlement_date DATE,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);
