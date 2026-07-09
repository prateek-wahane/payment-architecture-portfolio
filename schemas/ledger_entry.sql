CREATE TABLE ledger_entry (
  id BIGINT PRIMARY KEY,
  transaction_id VARCHAR(128) NOT NULL,
  account_id VARCHAR(128) NOT NULL,
  entry_type VARCHAR(16) NOT NULL,
  amount_minor BIGINT NOT NULL,
  currency CHAR(3) NOT NULL,
  event_type VARCHAR(64) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  UNIQUE (transaction_id, account_id, entry_type, event_type)
);
