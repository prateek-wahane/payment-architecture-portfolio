CREATE TABLE idempotency_record (
  idempotency_key VARCHAR(128) PRIMARY KEY,
  merchant_id BIGINT NOT NULL,
  request_hash VARCHAR(128) NOT NULL,
  response_payload TEXT,
  status VARCHAR(32) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  expires_at TIMESTAMP NOT NULL
);
