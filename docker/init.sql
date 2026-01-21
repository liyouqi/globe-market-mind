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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (source_id < target_id),
    UNIQUE(source_id, target_id, date)
);

-- Create indexes for performance
CREATE INDEX idx_daily_state_market ON daily_state(market_id);
CREATE INDEX idx_daily_state_date ON daily_state(date);
CREATE INDEX idx_correlation_edges_source ON correlation_edges(source_id);
CREATE INDEX idx_correlation_edges_target ON correlation_edges(target_id);
CREATE INDEX idx_correlation_edges_date ON correlation_edges(date);

-- Insert global markets (79 markets across 6 continents)
INSERT INTO market_registry (id, name, latitude, longitude, market_group, country) VALUES
    -- North America (10)
    ('US_SPX', 'S&P 500', 40.7128, -74.0060, 'DM', 'USA'),
    ('US_DJI', 'Dow Jones Industrial', 40.7128, -74.0060, 'DM', 'USA'),
    ('US_NASDAQ', 'Nasdaq Composite', 40.7128, -74.0060, 'DM', 'USA'),
    ('US_RUSSELL', 'Russell 2000', 40.7128, -74.0060, 'DM', 'USA'),
    ('US_SP400', 'S&P MidCap 400', 40.7128, -74.0060, 'DM', 'USA'),
    ('US_SP600', 'S&P SmallCap 600', 40.7128, -74.0060, 'DM', 'USA'),
    ('CA_TSX', 'Toronto TSX Composite', 43.6532, -79.3832, 'DM', 'Canada'),
    ('CA_TSX60', 'S&P/TSX 60', 43.6532, -79.3832, 'DM', 'Canada'),
    ('MX_IPC', 'Mexico IPC', 19.4326, -99.1332, 'EM', 'Mexico'),
    ('MX_INMEX', 'Mexico INMEX', 19.4326, -99.1332, 'EM', 'Mexico'),
    
    -- Europe (26)
    ('GB_FTSE', 'FTSE 100', 51.5074, -0.1278, 'DM', 'UK'),
    ('GB_FTSE250', 'FTSE 250', 51.5074, -0.1278, 'DM', 'UK'),
    ('DE_DAX', 'DAX', 50.1109, 8.6821, 'DM', 'Germany'),
    ('DE_MDAX', 'MDAX', 50.1109, 8.6821, 'DM', 'Germany'),
    ('FR_CAC', 'CAC 40', 48.8566, 2.3522, 'DM', 'France'),
    ('FR_SBF120', 'SBF 120', 48.8566, 2.3522, 'DM', 'France'),
    ('IT_FTSE', 'FTSE MIB', 45.4642, 9.1900, 'DM', 'Italy'),
    ('ES_IBEX', 'IBEX 35', 40.4168, -3.7038, 'DM', 'Spain'),
    ('NL_AEX', 'AEX', 52.3676, 4.9041, 'DM', 'Netherlands'),
    ('CH_SMI', 'SMI', 47.3769, 8.5417, 'DM', 'Switzerland'),
    ('SE_OMX', 'OMX Stockholm 30', 59.3293, 18.0686, 'DM', 'Sweden'),
    ('NO_OSE', 'Oslo Børs', 59.9139, 10.7522, 'DM', 'Norway'),
    ('DK_OMX', 'OMX Copenhagen', 55.6761, 12.5683, 'DM', 'Denmark'),
    ('FI_OMX', 'OMX Helsinki', 60.1695, 24.9354, 'DM', 'Finland'),
    ('BE_BEL', 'BEL 20', 50.8503, 4.3517, 'DM', 'Belgium'),
    ('AT_ATX', 'ATX', 48.2082, 16.3738, 'DM', 'Austria'),
    ('PL_WIG', 'WIG', 52.2297, 21.0122, 'EM', 'Poland'),
    ('CZ_PX', 'PX', 50.0755, 14.4378, 'EM', 'Czech Republic'),
    ('HU_BUX', 'BUX', 47.4979, 19.0402, 'EM', 'Hungary'),
    ('GR_ASE', 'Athens General', 37.9838, 23.7275, 'EM', 'Greece'),
    ('PT_PSI', 'PSI 20', 38.7223, -9.1393, 'DM', 'Portugal'),
    ('IE_ISEQ', 'ISEQ Overall', 53.3498, -6.2603, 'DM', 'Ireland'),
    ('RU_MOEX', 'MOEX', 55.7558, 37.6173, 'EM', 'Russia'),
    ('RU_RTS', 'RTS', 55.7558, 37.6173, 'EM', 'Russia'),
    ('TR_XU100', 'BIST 100', 41.0082, 28.9784, 'EM', 'Turkey'),
    ('EU_STOXX', 'Euro Stoxx 50', 50.1109, 8.6821, 'DM', 'Europe'),
    
    -- Asia-Pacific (25)
    ('JP_NIKKEI', 'Nikkei 225', 35.6762, 139.6503, 'DM', 'Japan'),
    ('JP_TOPIX', 'TOPIX', 35.6762, 139.6503, 'DM', 'Japan'),
    ('CN_SSE', 'Shanghai Composite', 31.2304, 121.4737, 'EM', 'China'),
    ('CN_SZSE', 'Shenzhen Component', 22.5431, 114.0579, 'EM', 'China'),
    ('CN_CSI300', 'CSI 300', 31.2304, 121.4737, 'EM', 'China'),
    ('HK_HSI', 'Hang Seng', 22.3193, 114.1694, 'DM', 'Hong Kong'),
    ('HK_HSCEI', 'Hang Seng China', 22.3193, 114.1694, 'DM', 'Hong Kong'),
    ('KR_KOSPI', 'KOSPI', 37.5665, 126.9780, 'EM', 'South Korea'),
    ('KR_KOSDAQ', 'KOSDAQ', 37.5665, 126.9780, 'EM', 'South Korea'),
    ('TW_TAIEX', 'TAIEX', 25.0330, 121.5654, 'EM', 'Taiwan'),
    ('IN_SENSEX', 'BSE Sensex', 18.9388, 72.8354, 'EM', 'India'),
    ('IN_NIFTY', 'Nifty 50', 28.6139, 77.2090, 'EM', 'India'),
    ('IN_NIFTY500', 'Nifty 500', 28.6139, 77.2090, 'EM', 'India'),
    ('SG_STI', 'Straits Times', 1.3521, 103.8198, 'DM', 'Singapore'),
    ('AU_ASX', 'ASX 200', -33.8688, 151.2093, 'DM', 'Australia'),
    ('AU_ALL', 'All Ordinaries', -33.8688, 151.2093, 'DM', 'Australia'),
    ('NZ_NZX', 'NZX 50', -36.8485, 174.7633, 'DM', 'New Zealand'),
    ('TH_SET', 'SET', 13.7563, 100.5018, 'EM', 'Thailand'),
    ('MY_KLSE', 'KLSE Composite', 3.1390, 101.6869, 'EM', 'Malaysia'),
    ('ID_JCI', 'Jakarta Composite', -6.2088, 106.8456, 'EM', 'Indonesia'),
    ('PH_PSE', 'PSE Composite', 14.5995, 120.9842, 'EM', 'Philippines'),
    ('VN_VNI', 'VN Index', 10.8231, 106.6297, 'EM', 'Vietnam'),
    ('PK_KSE', 'KSE 100', 24.8607, 67.0011, 'EM', 'Pakistan'),
    ('BD_DSE', 'DSE General', 23.8103, 90.4125, 'EM', 'Bangladesh'),
    ('LK_CSE', 'CSE All-Share', 6.9271, 79.8612, 'EM', 'Sri Lanka'),
    
    -- Latin America (8)
    ('BR_IBOV', 'Bovespa', -23.5505, -46.6333, 'EM', 'Brazil'),
    ('AR_MERV', 'Merval', -34.6037, -58.3816, 'EM', 'Argentina'),
    ('CL_IPSA', 'IPSA', -33.4489, -70.6693, 'EM', 'Chile'),
    ('CO_COLCAP', 'COLCAP', 4.7110, -74.0721, 'EM', 'Colombia'),
    ('PE_SPBLPGPT', 'Lima General', -12.0464, -77.0428, 'EM', 'Peru'),
    ('VE_IBC', 'IBC', 10.4806, -66.9036, 'EM', 'Venezuela'),
    ('CR_CRSMBCT', 'Costa Rica Index', 9.9281, -84.0907, 'EM', 'Costa Rica'),
    ('JM_JSE', 'Jamaica Index', 18.0179, -76.8099, 'EM', 'Jamaica'),
    
    -- Middle East (6)
    ('IL_TA125', 'TA-125', 32.0853, 34.7818, 'DM', 'Israel'),
    ('SA_TASI', 'Tadawul All Share', 24.7136, 46.6753, 'EM', 'Saudi Arabia'),
    ('AE_ADX', 'Abu Dhabi General', 24.4539, 54.3773, 'EM', 'UAE'),
    ('AE_DFM', 'Dubai Financial Market', 25.2048, 55.2708, 'EM', 'UAE'),
    ('QA_DSM', 'Qatar DSM 20', 25.2854, 51.5310, 'EM', 'Qatar'),
    ('KW_BKP', 'Kuwait BKP', 29.3759, 47.9774, 'EM', 'Kuwait'),
    
    -- Africa (4)
    ('ZA_JSE', 'JSE Top 40', -26.2041, 28.0473, 'EM', 'South Africa'),
    ('ZA_JALSH', 'JSE All Share', -26.2041, 28.0473, 'EM', 'South Africa'),
    ('EG_EGX', 'EGX 30', 30.0444, 31.2357, 'EM', 'Egypt'),
    ('MA_MASI', 'MASI', 33.5731, -7.5898, 'EM', 'Morocco')
ON CONFLICT DO NOTHING;
