CREATE TABLE events (
    id         BIGSERIAL PRIMARY KEY,
    kind       TEXT        NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
