-- 0002 timed out in production; run it again so every environment has the index.
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_events_created ON events (created_at);
