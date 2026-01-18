-- Create market_registry table
CREATE TABLE IF NOT EXISTS market_registry (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    market_group VARCHAR(50) NOT NULL CHECK (market_group IN ('DM', 'EM')),
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create daily_state table
CREATE TABLE IF NOT EXISTS daily_state (
    id SERIAL PRIMARY KEY,
    market_id VARCHAR(50) NOT NULL REFERENCES market_registry(id),
    date DATE NOT NULL,
    close_price FLOAT NOT NULL,
    volume BIGINT,
    change_pct FLOAT,
    mood_index FLOAT,
    mood_level VARCHAR(20),
    volatility_30d FLOAT,
    trend_strength FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(market_id, date)
);

-- Create correlation_edges table
CREATE TABLE IF NOT EXISTS correlation_edges (
    id SERIAL PRIMARY KEY,
    source_id VARCHAR(50) NOT NULL REFERENCES market_registry(id),
    target_id VARCHAR(50) NOT NULL REFERENCES market_registry(id),
    correlation_value FLOAT NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (source_id < target_id),
    UNIQUE(source_id, target_id, date)
);

-- Create indexes for performance
CREATE INDEX idx_daily_state_market ON daily_state(market_id);
CREATE INDEX idx_daily_state_date ON daily_state(date);
CREATE INDEX idx_correlation_edges_source ON correlation_edges(source_id);
CREATE INDEX idx_correlation_edges_target ON correlation_edges(target_id);

-- Insert major global markets
INSERT INTO market_registry (id, name, latitude, longitude, market_group, country) VALUES
    ('US_SPX', 'S&P 500', 40.7128, -74.0060, 'DM', 'USA'),
    ('US_IYY', 'Dow Jones', 40.7128, -74.0060, 'DM', 'USA'),
    ('US_CCMP', 'Nasdaq', 40.7128, -74.0060, 'DM', 'USA'),
    ('EU_STOXX', 'STOXX Europe 600', 48.8566, 2.3522, 'DM', 'Europe'),
    ('GB_FTSE', 'FTSE 100', 51.5074, -0.1278, 'DM', 'UK'),
    ('JP_NIKKEI', 'Nikkei 225', 35.6762, 139.6503, 'DM', 'Japan'),
    ('CN_SSE', 'Shanghai Composite', 31.2304, 121.4737, 'EM', 'China'),
    ('IN_SENSEX', 'BSE Sensex', 19.0760, 72.8777, 'EM', 'India'),
    ('BR_IBOV', 'Bovespa', -23.5505, -46.6333, 'EM', 'Brazil'),
    ('KR_KOSPI', 'KOSPI', 37.4979, 127.0276, 'EM', 'South Korea'),
    ('RU_MOEX', 'MOEX Russia', 55.7558, 37.6173, 'EM', 'Russia'),
    ('AU_ASX', 'ASX 200', -33.8688, 151.2093, 'DM', 'Australia'),
    ('CH_SMI', 'SMI', 47.3769, 8.5472, 'DM', 'Switzerland'),
    ('SG_STI', 'Straits Times', 1.3521, 103.8198, 'EM', 'Singapore'),
    ('MX_MEXBOL', 'IPC Mexico', 19.4326, -99.1332, 'EM', 'Mexico')
ON CONFLICT DO NOTHING;
