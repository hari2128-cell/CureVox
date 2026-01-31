-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create additional roles if needed
-- CREATE ROLE read_only;
-- GRANT CONNECT ON DATABASE curevox_db TO read_only;
-- GRANT USAGE ON SCHEMA public TO read_only;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO read_only;

-- Set up performance configurations
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '768MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.7;
ALTER SYSTEM SET wal_buffers = '4MB';
ALTER SYSTEM SET default_statistics_target = 100;