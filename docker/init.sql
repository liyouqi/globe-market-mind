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
    
    -- Africa (35) - Complete continental coverage
    -- Southern Africa
    ('ZA_JSE', 'JSE Top 40', -26.2041, 28.0473, 'EM', 'South Africa'),
    ('ZA_JALSH', 'JSE All Share', -26.2041, 28.0473, 'EM', 'South Africa'),
    ('BW_BSE', 'Botswana Stock Exchange', -24.6282, 25.9231, 'EM', 'Botswana'),
    ('ZM_LUSE', 'Lusaka Securities Exchange', -15.3875, 28.3228, 'EM', 'Zambia'),
    ('ZW_ZSE', 'Zimbabwe Stock Exchange', -17.8252, 31.0335, 'EM', 'Zimbabwe'),
    ('NA_NSX', 'Namibian Stock Exchange', -22.5609, 17.0658, 'EM', 'Namibia'),
    ('MZ_BVM', 'Mozambique Stock Exchange', -25.9692, 32.5732, 'EM', 'Mozambique'),
    ('MW_MSE', 'Malawi Stock Exchange', -13.9626, 33.7741, 'EM', 'Malawi'),
    ('AO_BVDA', 'Angola Stock Exchange', -8.8383, 13.2344, 'EM', 'Angola'),
    ('SZ_SSX', 'Eswatini Stock Exchange', -26.3054, 31.1367, 'EM', 'Eswatini'),
    ('LS_MSM', 'Lesotho Stock Market', -29.3167, 27.4833, 'EM', 'Lesotho'),
    
    -- East Africa
    ('KE_NSE', 'Nairobi Securities Exchange', -1.2864, 36.8172, 'EM', 'Kenya'),
    ('UG_USE', 'Uganda Securities Exchange', 0.3476, 32.5825, 'EM', 'Uganda'),
    ('TZ_DSE', 'Dar es Salaam Stock Exchange', -6.7924, 39.2083, 'EM', 'Tanzania'),
    ('RW_RSE', 'Rwanda Stock Exchange', -1.9403, 29.8739, 'EM', 'Rwanda'),
    ('ET_ESX', 'Ethiopian Securities Exchange', 9.0320, 38.7469, 'EM', 'Ethiopia'),
    ('MU_SEMDEX', 'SEMDEX', -20.1609, 57.5012, 'EM', 'Mauritius'),
    ('SO_SSE', 'Somalia Stock Exchange', 2.0469, 45.3182, 'EM', 'Somalia'),
    ('DJ_DSE', 'Djibouti Stock Exchange', 11.8251, 42.5903, 'EM', 'Djibouti'),
    ('ER_ESE', 'Eritrea Stock Exchange', 15.3229, 38.9251, 'EM', 'Eritrea'),
    ('SC_SSE', 'Seychelles Stock Exchange', -4.6796, 55.4920, 'EM', 'Seychelles'),
    
    -- North Africa
    ('EG_EGX', 'EGX 30', 30.0444, 31.2357, 'EM', 'Egypt'),
    ('MA_MASI', 'MASI', 33.5731, -7.5898, 'EM', 'Morocco'),
    ('TN_TUNINDEX', 'Tunindex', 36.8065, 10.1815, 'EM', 'Tunisia'),
    ('DZ_DZAIRINDEX', 'Algiers Stock Exchange', 36.7538, 3.0588, 'EM', 'Algeria'),
    ('LY_LSM', 'Libya Stock Market', 32.8872, 13.1913, 'EM', 'Libya'),
    ('SD_KSE', 'Khartoum Stock Exchange', 15.5007, 32.5599, 'EM', 'Sudan'),
    
    -- West Africa
    ('NG_NSE', 'Nigerian Stock Exchange', 6.4541, 3.3947, 'EM', 'Nigeria'),
    ('GH_GSE', 'Ghana Stock Exchange', 5.6037, -0.1870, 'EM', 'Ghana'),
    ('CI_BRVM', 'BRVM Abidjan', 5.3600, -4.0083, 'EM', 'Ivory Coast'),
    ('SN_BRVM', 'BRVM Dakar', 14.7167, -17.4677, 'EM', 'Senegal'),
    ('BJ_BRVM', 'BRVM Benin', 6.4969, 2.6289, 'EM', 'Benin'),
    ('CM_DSX', 'Douala Stock Exchange', 4.0511, 9.7679, 'EM', 'Cameroon'),
    ('NE_NSE', 'Niger Stock Exchange', 13.5127, 2.1126, 'EM', 'Niger'),
    ('BF_BRVM', 'BRVM Burkina Faso', 12.3714, -1.5197, 'EM', 'Burkina Faso'),
    
    -- Additional Europe (15) - Eastern Europe, Balkans, Baltics
    ('RO_BET', 'BET', 44.4268, 26.1025, 'EM', 'Romania'),
    ('BG_SOFIX', 'SOFIX', 42.6977, 23.3219, 'EM', 'Bulgaria'),
    ('HR_CROBEX', 'CROBEX', 45.8150, 15.9819, 'EM', 'Croatia'),
    ('SI_SBITOP', 'SBITOP', 46.0569, 14.5058, 'EM', 'Slovenia'),
    ('RS_BELEX', 'BELEX15', 44.7866, 20.4489, 'EM', 'Serbia'),
    ('SK_SAX', 'SAX', 48.1486, 17.1077, 'EM', 'Slovakia'),
    ('LT_OMXV', 'OMX Vilnius', 54.6872, 25.2797, 'EM', 'Lithuania'),
    ('LV_OMXR', 'OMX Riga', 56.9496, 24.1052, 'EM', 'Latvia'),
    ('EE_OMXT', 'OMX Tallinn', 59.4370, 24.7536, 'EM', 'Estonia'),
    ('UA_PFTS', 'PFTS', 50.4501, 30.5234, 'EM', 'Ukraine'),
    ('IS_ICEX', 'ICEX Main', 64.1466, -21.9426, 'DM', 'Iceland'),
    ('LU_LUXX', 'LuxX', 49.6116, 6.1319, 'DM', 'Luxembourg'),
    ('MT_MSE', 'Malta Stock Exchange', 35.8989, 14.5146, 'EM', 'Malta'),
    ('CY_CSE', 'Cyprus Stock Exchange', 35.1264, 33.4299, 'EM', 'Cyprus'),
    ('MK_MSE', 'Macedonia Stock Exchange', 41.9973, 21.4280, 'EM', 'North Macedonia'),
    
    -- Additional Middle East & Central Asia (10)
    ('JO_ASE', 'Amman Stock Exchange', 31.9454, 35.9284, 'EM', 'Jordan'),
    ('LB_BLOM', 'BLOM Stock Index', 33.8886, 35.4955, 'EM', 'Lebanon'),
    ('OM_MSM', 'Muscat Securities Market', 23.5880, 58.3829, 'EM', 'Oman'),
    ('BH_BAX', 'Bahrain All Share', 26.0667, 50.5577, 'EM', 'Bahrain'),
    ('PS_PSE', 'Palestine Securities Exchange', 31.9522, 35.2332, 'EM', 'Palestine'),
    ('KZ_KASE', 'Kazakhstan Stock Exchange', 43.2220, 76.8512, 'EM', 'Kazakhstan'),
    ('UZ_UZSE', 'Uzbekistan Stock Exchange', 41.2995, 69.2401, 'EM', 'Uzbekistan'),
    ('GE_GSE', 'Georgia Stock Exchange', 41.7151, 44.8271, 'EM', 'Georgia'),
    ('AM_AMX', 'Armenia Stock Exchange', 40.1792, 44.4991, 'EM', 'Armenia'),
    ('AZ_AZSE', 'Azerbaijan Stock Exchange', 40.4093, 49.8671, 'EM', 'Azerbaijan'),
    
    -- Additional Asia-Pacific (12)
    ('MN_MSE', 'Mongolian Stock Exchange', 47.8864, 106.9057, 'EM', 'Mongolia'),
    ('KH_CSX', 'Cambodia Securities Exchange', 11.5564, 104.9282, 'EM', 'Cambodia'),
    ('LA_LSX', 'Lao Securities Exchange', 17.9757, 102.6331, 'EM', 'Laos'),
    ('MM_YSX', 'Yangon Stock Exchange', 16.8661, 96.1951, 'EM', 'Myanmar'),
    ('NP_NEPSE', 'Nepal Stock Exchange', 27.7172, 85.3240, 'EM', 'Nepal'),
    ('BT_RSE', 'Royal Securities Exchange', 27.4728, 89.6393, 'EM', 'Bhutan'),
    ('MV_MSE', 'Maldives Stock Exchange', 4.1755, 73.5093, 'EM', 'Maldives'),
    ('BN_BSE', 'Brunei Stock Exchange', 4.9031, 114.9398, 'EM', 'Brunei'),
    ('FJ_SPX', 'South Pacific Stock Exchange', -18.1248, 178.4501, 'EM', 'Fiji'),
    ('PG_PNGX', 'Port Moresby Stock Exchange', -9.4438, 147.1803, 'EM', 'Papua New Guinea'),
    ('MO_MSE', 'Macau Stock Exchange', 22.1987, 113.5439, 'EM', 'Macau'),
    ('TL_TLSE', 'Timor-Leste Stock Exchange', -8.5569, 125.5603, 'EM', 'Timor-Leste'),
    
    -- Additional Latin America & Caribbean (14)
    ('UY_ BOLSA', 'Montevideo Stock Exchange', -34.9011, -56.1645, 'EM', 'Uruguay'),
    ('PY_BVPASA', 'Asuncion Stock Exchange', -25.2637, -57.5759, 'EM', 'Paraguay'),
    ('BO_BOLSA', 'Bolivian Stock Exchange', -16.5000, -68.1500, 'EM', 'Bolivia'),
    ('EC_IPEC', 'Quito Stock Exchange', -0.1807, -78.4678, 'EM', 'Ecuador'),
    ('PA_BVPAN', 'Panama Stock Exchange', 8.9824, -79.5199, 'EM', 'Panama'),
    ('SV_BVES', 'El Salvador Stock Exchange', 13.6929, -89.2182, 'EM', 'El Salvador'),
    ('GT_BVG', 'Guatemala Stock Exchange', 14.6349, -90.5069, 'EM', 'Guatemala'),
    ('HN_BVH', 'Honduras Stock Exchange', 14.0723, -87.1921, 'EM', 'Honduras'),
    ('NI_BVDN', 'Nicaragua Stock Exchange', 12.1150, -86.2362, 'EM', 'Nicaragua'),
    ('DO_BVRD', 'Dominican Republic Stock Exchange', 18.4861, -69.9312, 'EM', 'Dominican Republic'),
    ('TT_TTSE', 'Trinidad & Tobago Stock Exchange', 10.6918, -61.2225, 'EM', 'Trinidad & Tobago'),
    ('BB_BSE', 'Barbados Stock Exchange', 13.1939, -59.5432, 'EM', 'Barbados'),
    ('BS_BISX', 'Bahamas International Securities', 25.0443, -77.3504, 'EM', 'Bahamas'),
    ('BM_BSX', 'Bermuda Stock Exchange', 32.3078, -64.7505, 'EM', 'Bermuda')
ON CONFLICT DO NOTHING;
