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

-- One comparison per successful load; history starts when this feature is installed.
CREATE TABLE IF NOT EXISTS revision_runs (
    revision_id VARCHAR PRIMARY KEY,
    retrieval_id VARCHAR NOT NULL REFERENCES ingestion_runs(retrieval_id),
    loaded_at TIMESTAMPTZ NOT NULL,
    mode VARCHAR NOT NULL CHECK (mode IN ('live', 'replay')),
    previous_retrieval_ids VARCHAR[] NOT NULL,
    generation_added INTEGER NOT NULL CHECK (generation_added >= 0),
    generation_changed INTEGER NOT NULL CHECK (generation_changed >= 0),
    generation_removed INTEGER NOT NULL CHECK (generation_removed >= 0),
    generation_unchanged INTEGER NOT NULL CHECK (generation_unchanged >= 0),
    totals_added INTEGER NOT NULL CHECK (totals_added >= 0),
    totals_changed INTEGER NOT NULL CHECK (totals_changed >= 0),
    totals_removed INTEGER NOT NULL CHECK (totals_removed >= 0),
    totals_unchanged INTEGER NOT NULL CHECK (totals_unchanged >= 0)
);
