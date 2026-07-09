CREATE TABLE webhook_event (
  id BIGINT PRIMARY KEY,
  provider VARCHAR(64) NOT NULL,
  provider_event_id VARCHAR(128) NOT NULL,
  provider_txn_id VARCHAR(128),
  event_type VARCHAR(64) NOT NULL,
  raw_payload TEXT NOT NULL,
  signature_valid BOOLEAN NOT NULL,
  processed_status VARCHAR(32) NOT NULL,
  received_at TIMESTAMP NOT NULL,
  UNIQUE (provider, provider_event_id)
);
