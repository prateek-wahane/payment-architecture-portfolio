CREATE TABLE payment_attempt (
  id BIGINT PRIMARY KEY,
  payment_order_id BIGINT NOT NULL,
  provider VARCHAR(64) NOT NULL,
  provider_txn_id VARCHAR(128),
  payment_method VARCHAR(32) NOT NULL,
  status VARCHAR(32) NOT NULL,
  request_hash VARCHAR(128) NOT NULL,
  error_code VARCHAR(64),
  error_message VARCHAR(512),
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  UNIQUE (provider, provider_txn_id)
);
