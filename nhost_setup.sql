-- Create the table for storing Yahoo Finance analysis data in Nhost
-- Run this in your Nhost Hasura console or SQL editor

CREATE TABLE IF NOT EXISTS yahoo_finance_data (
    id BIGSERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    scraped_at TIMESTAMPTZ NOT NULL,
    url TEXT NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_yahoo_finance_data_ticker ON yahoo_finance_data(ticker);
CREATE INDEX IF NOT EXISTS idx_yahoo_finance_data_scraped_at ON yahoo_finance_data(scraped_at);
CREATE INDEX IF NOT EXISTS idx_yahoo_finance_data_created_at ON yahoo_finance_data(created_at);

-- Create a GIN index on the JSONB data field for efficient JSON queries
CREATE INDEX IF NOT EXISTS idx_yahoo_finance_data_data_gin ON yahoo_finance_data USING GIN (data);

-- Enable Row Level Security (RLS) - optional but recommended
ALTER TABLE yahoo_finance_data ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations (you can restrict this based on your needs)
CREATE POLICY "Allow all operations on yahoo_finance_data" ON yahoo_finance_data
    FOR ALL USING (true);

-- Optional: Create a view for recent scrapes
CREATE OR REPLACE VIEW recent_yahoo_finance_data AS
SELECT 
    ticker,
    scraped_at,
    url,
    data,
    created_at
FROM yahoo_finance_data
WHERE scraped_at >= NOW() - INTERVAL '7 days'
ORDER BY scraped_at DESC;

-- Optional: Create a view for latest data per ticker
CREATE OR REPLACE VIEW latest_yahoo_finance_data AS
SELECT DISTINCT ON (ticker)
    ticker,
    scraped_at,
    url,
    data,
    created_at
FROM yahoo_finance_data
ORDER BY ticker, scraped_at DESC;

-- Grant permissions to the hasura role (Nhost uses this by default)
GRANT ALL ON TABLE yahoo_finance_data TO hasura;
GRANT ALL ON SEQUENCE yahoo_finance_data_id_seq TO hasura;
GRANT ALL ON VIEW recent_yahoo_finance_data TO hasura;
GRANT ALL ON VIEW latest_yahoo_finance_data TO hasura; 