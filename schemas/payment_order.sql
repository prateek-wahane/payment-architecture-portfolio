CREATE TABLE payment_order (
  id BIGINT PRIMARY KEY,
  merchant_id BIGINT NOT NULL,
  order_id VARCHAR(64) NOT NULL,
  customer_id BIGINT,
  amount_minor BIGINT NOT NULL,
  currency CHAR(3) NOT NULL,
  status VARCHAR(32) NOT NULL,
  idempotency_key VARCHAR(128) NOT NULL,
  version BIGINT NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  UNIQUE (merchant_id, order_id),
  UNIQUE (merchant_id, idempotency_key)
);
