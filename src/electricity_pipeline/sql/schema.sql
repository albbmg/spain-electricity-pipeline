CREATE TABLE IF NOT EXISTS ingestion_runs (
    retrieval_id VARCHAR PRIMARY KEY,
    source_url VARCHAR NOT NULL,
    region VARCHAR NOT NULL CHECK (region = 'peninsular'),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    retrieved_at TIMESTAMPTZ NOT NULL,
    source_updated_at TIMESTAMPTZ NOT NULL,
    sha256 VARCHAR NOT NULL,
    raw_file VARCHAR NOT NULL,
    observation_count INTEGER NOT NULL CHECK (observation_count > 0)
);

-- Additive: older warehouses keep their original schema and retrieval timestamps.
CREATE TABLE IF NOT EXISTS replay_runs (
    replay_id VARCHAR PRIMARY KEY,
    retrieval_id VARCHAR NOT NULL REFERENCES ingestion_runs(retrieval_id),
    replayed_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS generation (
    region VARCHAR NOT NULL CHECK (region = 'peninsular'),
    day DATE NOT NULL,
    technology_id VARCHAR NOT NULL,
    technology VARCHAR NOT NULL,
    renewable BOOLEAN NOT NULL,
    energy_mwh DECIMAL(24,6) NOT NULL CHECK (energy_mwh >= 0),
    source_share DOUBLE,
    source_updated_at TIMESTAMPTZ NOT NULL,
    retrieval_id VARCHAR NOT NULL,
    PRIMARY KEY (region, day, technology_id)
);

CREATE TABLE IF NOT EXISTS source_totals (
    region VARCHAR NOT NULL CHECK (region = 'peninsular'),
    day DATE NOT NULL,
    total_mwh DECIMAL(24,6) NOT NULL CHECK (total_mwh > 0),
    retrieval_id VARCHAR NOT NULL,
    PRIMARY KEY (region, day)
);
