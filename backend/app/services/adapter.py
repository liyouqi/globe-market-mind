"""
Adapter Service - Fetch market data from external data sources
Currently supports Yahoo Finance API via yfinance
"""

import yfinance as yf
from datetime import datetime, timedelta
import logging
import random

logger = logging.getLogger(__name__)

class YahooFinanceAdapter:
    """Yahoo Finance data adapter"""
    
    # Market symbol mapping - Global Coverage (70+ markets)
    MARKET_SYMBOLS = {
        # === NORTH AMERICA (10) ===
        'US_SPX': '^GSPC',       # S&P 500
        'US_DJI': '^DJI',        # Dow Jones Industrial Average
        'US_NASDAQ': '^IXIC',    # Nasdaq Composite
        'US_RUSSELL': '^RUT',    # Russell 2000
        'US_SP400': '^MID',      # S&P MidCap 400
        'US_SP600': '^SML',      # S&P SmallCap 600
        'CA_TSX': '^GSPTSE',     # Toronto S&P/TSX Composite
        'CA_TSX60': '^TX60',     # S&P/TSX 60
        'MX_IPC': '^MXX',        # Mexico IPC
        'MX_INMEX': '^INMEX',    # Mexico INMEX
        
        # === EUROPE (26) ===
        'GB_FTSE': '^FTSE',      # UK FTSE 100
        'GB_FTSE250': '^FTMC',   # UK FTSE 250
        'DE_DAX': '^GDAXI',      # Germany DAX
        'DE_MDAX': '^MDAXI',     # Germany MDAX
        'FR_CAC': '^FCHI',       # France CAC 40
        'FR_SBF120': '^SBF120',  # France SBF 120
        'IT_FTSE': 'FTSEMIB.MI', # Italy FTSE MIB
        'ES_IBEX': '^IBEX',      # Spain IBEX 35
        'NL_AEX': '^AEX',        # Netherlands AEX
        'CH_SMI': '^SSMI',       # Switzerland SMI
        'SE_OMX': '^OMX',        # Sweden OMX Stockholm 30
        'NO_OSE': 'OSEBX.OL',    # Norway Oslo Børs
        'DK_OMX': '^OMXC25',     # Denmark OMX Copenhagen
        'FI_OMX': '^OMXH25',     # Finland OMX Helsinki
        'BE_BEL': '^BFX',        # Belgium BEL 20
        'AT_ATX': '^ATX',        # Austria ATX
        'PL_WIG': '^WIG',        # Poland WIG
        'CZ_PX': '^PX',          # Czech Republic PX
        'HU_BUX': '^BUX',        # Hungary BUX
        'GR_ASE': 'ASEG.AT',     # Greece Athens General
        'PT_PSI': '^PSI20',      # Portugal PSI 20
        'IE_ISEQ': '^ISEQ',      # Ireland ISEQ Overall
        'RU_MOEX': 'IMOEX.ME',   # Russia MOEX
        'RU_RTS': '^RTSI',       # Russia RTS
        'TR_XU100': 'XU100.IS',  # Turkey BIST 100
        'EU_STOXX': '^STOXX50E', # Euro Stoxx 50
        
        # === ASIA-PACIFIC (25) ===
        'JP_NIKKEI': '^N225',    # Japan Nikkei 225
        'JP_TOPIX': '^TPX',      # Japan TOPIX
        'CN_SSE': '000001.SS',   # China Shanghai Composite
        'CN_SZSE': '399001.SZ',  # China Shenzhen Component
        'CN_CSI300': '000300.SS',# China CSI 300
        'HK_HSI': '^HSI',        # Hong Kong Hang Seng
        'HK_HSCEI': '^HSCE',     # Hong Kong H-Share
        'KR_KOSPI': '^KS11',     # South Korea KOSPI
        'KR_KOSDAQ': '^KQ11',    # South Korea KOSDAQ
        'TW_TAIEX': '^TWII',     # Taiwan TAIEX
        'IN_SENSEX': '^BSESN',   # India BSE Sensex
        'IN_NIFTY': '^NSEI',     # India Nifty 50
        'IN_NIFTY500': '^CRSLDX',# India Nifty 500
        'SG_STI': '^STI',        # Singapore Straits Times
        'AU_ASX': '^AXJO',       # Australia ASX 200
        'AU_ALL': '^AORD',       # Australia All Ordinaries
        'NZ_NZX': '^NZ50',       # New Zealand NZX 50
        'TH_SET': '^SET.BK',     # Thailand SET
        'MY_KLSE': '^KLSE',      # Malaysia KLSE Composite
        'ID_JCI': '^JKSE',       # Indonesia Jakarta Composite
        'PH_PSE': '^PSI',        # Philippines PSE Composite
        'VN_VNI': '^VNINDEX',    # Vietnam VN Index
        'PK_KSE': 'KSE100.KA',   # Pakistan KSE 100
        'BD_DSE': '^DSEX',       # Bangladesh Dhaka Stock Exchange
        'LK_CSE': '^CSEALL',     # Sri Lanka Colombo All-Share
        
        # === LATIN AMERICA (8) ===
        'BR_IBOV': '^BVSP',      # Brazil Bovespa
        'AR_MERV': '^MERV',      # Argentina Merval
        'CL_IPSA': '^IPSA',      # Chile IPSA
        'CO_COLCAP': '^COLCAP',  # Colombia COLCAP
        'PE_SPBLPGPT': '^SPBLPGPT', # Peru Lima General
        'VE_IBC': '^IBC',        # Venezuela IBC
        'CR_CRSMBCT': '^CRSMBCT',# Costa Rica CRSMBCT
        'JM_JSE': '^JMAI',       # Jamaica JSE Market Index
        
        # === MIDDLE EAST (6) ===
        'IL_TA125': '^TA125.TA', # Israel TA-125
        'SA_TASI': '^TASI.SR',   # Saudi Arabia Tadawul All Share
        'AE_ADX': '^ADI',        # UAE Abu Dhabi General
        'AE_DFM': '^DFMGI',      # UAE Dubai Financial Market
        'QA_DSM': '^DSM',        # Qatar DSM 20
        'KW_BKP': '^BKP',        # Kuwait BKP
        
        # === AFRICA (35) ===
        # Southern Africa
        'ZA_JSE': '^JN0U.JO',    # South Africa JSE Top 40
        'ZA_JALSH': '^J203.JO',  # South Africa JSE All Share
        'BW_BSE': 'BSE.BW',      # Botswana
        'ZM_LUSE': 'LUSE.ZM',    # Zambia
        'ZW_ZSE': 'ZSE.ZW',      # Zimbabwe
        'NA_NSX': 'NSX.NA',      # Namibia
        'MZ_BVM': 'BVM.MZ',      # Mozambique
        'MW_MSE': 'MSE.MW',      # Malawi
        'AO_BVDA': 'BVDA.AO',    # Angola
        'SZ_SSX': 'SSX.SZ',      # Eswatini
        'LS_MSM': 'MSM.LS',      # Lesotho
        # East Africa
        'KE_NSE': 'NSE.KE',      # Kenya
        'UG_USE': 'USE.UG',      # Uganda
        'TZ_DSE': 'DSE.TZ',      # Tanzania
        'RW_RSE': 'RSE.RW',      # Rwanda
        'ET_ESX': 'ESX.ET',      # Ethiopia
        'MU_SEMDEX': 'SEMDEX.MU',# Mauritius
        'SO_SSE': 'SSE.SO',      # Somalia
        'DJ_DSE': 'DSE.DJ',      # Djibouti
        'ER_ESE': 'ESE.ER',      # Eritrea
        'SC_SSE': 'SSE.SC',      # Seychelles
        # North Africa
        'EG_EGX': '^CASE30',     # Egypt
        'MA_MASI': '^MASI.CS',   # Morocco
        'TN_TUNINDEX': 'TUNINDEX.TN', # Tunisia
        'DZ_DZAIRINDEX': 'DZAIR.DZ',  # Algeria
        'LY_LSM': 'LSM.LY',      # Libya
        'SD_KSE': 'KSE.SD',      # Sudan
        # West Africa
        'NG_NSE': 'NSE.NG',      # Nigeria
        'GH_GSE': 'GSE.GH',      # Ghana
        'CI_BRVM': 'BRVM.CI',    # Ivory Coast
        'SN_BRVM': 'BRVM.SN',    # Senegal
        'BJ_BRVM': 'BRVM.BJ',    # Benin
        'CM_DSX': 'DSX.CM',      # Cameroon
        'NE_NSE': 'NSE.NE',      # Niger
        'BF_BRVM': 'BRVM.BF',    # Burkina Faso
        
        # === ADDITIONAL EUROPE (15) ===
        'RO_BET': '^BET',        # Romania
        'BG_SOFIX': '^SOFIX',    # Bulgaria
        'HR_CROBEX': '^CROBEX',  # Croatia
        'SI_SBITOP': '^SBITOP',  # Slovenia
        'RS_BELEX': '^BELEX15',  # Serbia
        'SK_SAX': '^SAX',        # Slovakia
        'LT_OMXV': '^OMXVGI',    # Lithuania
        'LV_OMXR': '^OMXRGI',    # Latvia
        'EE_OMXT': '^OMXTGI',    # Estonia
        'UA_PFTS': '^PFTS',      # Ukraine
        'IS_ICEX': '^ICEXI',     # Iceland
        'LU_LUXX': '^LUXX',      # Luxembourg
        'MT_MSE': 'MSE.MT',      # Malta
        'CY_CSE': 'CSE.CY',      # Cyprus
        'MK_MSE': 'MSE.MK',      # North Macedonia
        
        # === ADDITIONAL MIDDLE EAST & CENTRAL ASIA (10) ===
        'JO_ASE': 'ASE.JO',      # Jordan
        'LB_BLOM': 'BLOM.LB',    # Lebanon
        'OM_MSM': 'MSM.OM',      # Oman
        'BH_BAX': 'BAX.BH',      # Bahrain
        'PS_PSE': 'PSE.PS',      # Palestine
        'KZ_KASE': 'KASE.KZ',    # Kazakhstan
        'UZ_UZSE': 'UZSE.UZ',    # Uzbekistan
        'GE_GSE': 'GSE.GE',      # Georgia
        'AM_AMX': 'AMX.AM',      # Armenia
        'AZ_AZSE': 'AZSE.AZ',    # Azerbaijan
        
        # === ADDITIONAL ASIA-PACIFIC (12) ===
        'MN_MSE': 'MSE.MN',      # Mongolia
        'KH_CSX': 'CSX.KH',      # Cambodia
        'LA_LSX': 'LSX.LA',      # Laos
        'MM_YSX': 'YSX.MM',      # Myanmar
        'NP_NEPSE': 'NEPSE.NP',  # Nepal
        'BT_RSE': 'RSE.BT',      # Bhutan
        'MV_MSE': 'MSE.MV',      # Maldives
        'BN_BSE': 'BSE.BN',      # Brunei
        'FJ_SPX': 'SPX.FJ',      # Fiji
        'PG_PNGX': 'PNGX.PG',    # Papua New Guinea
        'MO_MSE': 'MSE.MO',      # Macau
        'TL_TLSE': 'TLSE.TL',    # Timor-Leste
        
        # === ADDITIONAL LATIN AMERICA & CARIBBEAN (14) ===
        'UY_ BOLSA': 'BOLSA.UY', # Uruguay
        'PY_BVPASA': 'BVPASA.PY',# Paraguay
        'BO_BOLSA': 'BOLSA.BO',  # Bolivia
        'EC_IPEC': 'IPEC.EC',    # Ecuador
        'PA_BVPAN': 'BVPAN.PA',  # Panama
        'SV_BVES': 'BVES.SV',    # El Salvador
        'GT_BVG': 'BVG.GT',      # Guatemala
        'HN_BVH': 'BVH.HN',      # Honduras
        'NI_BVDN': 'BVDN.NI',    # Nicaragua
        'DO_BVRD': 'BVRD.DO',    # Dominican Republic
        'TT_TTSE': '^TTSE',      # Trinidad & Tobago
        'BB_BSE': 'BSE.BB',      # Barbados
        'BS_BISX': 'BISX.BS',    # Bahamas
        'BM_BSX': '^BSX',        # Bermuda
    }
    
    # Mock prices for testing - Realistic base values (as of Jan 2026)
    MOCK_PRICES = {
        # North America
        'US_SPX': 4500.0, 'US_DJI': 35000.0, 'US_NASDAQ': 14000.0, 'US_RUSSELL': 1900.0,
        'US_SP400': 2800.0, 'US_SP600': 1300.0, 'CA_TSX': 20000.0, 'CA_TSX60': 1200.0,
        'MX_IPC': 52000.0, 'MX_INMEX': 25000.0,
        
        # Europe
        'GB_FTSE': 7700.0, 'GB_FTSE250': 19000.0, 'DE_DAX': 16500.0, 'DE_MDAX': 27000.0,
        'FR_CAC': 7300.0, 'FR_SBF120': 5500.0, 'IT_FTSE': 28000.0, 'ES_IBEX': 9500.0,
        'NL_AEX': 800.0, 'CH_SMI': 11200.0, 'SE_OMX': 2400.0, 'NO_OSE': 1300.0,
        'DK_OMX': 2100.0, 'FI_OMX': 5500.0, 'BE_BEL': 3800.0, 'AT_ATX': 3500.0,
        'PL_WIG': 65000.0, 'CZ_PX': 1400.0, 'HU_BUX': 50000.0, 'GR_ASE': 1200.0,
        'PT_PSI': 6000.0, 'IE_ISEQ': 9500.0, 'RU_MOEX': 3000.0, 'RU_RTS': 1100.0,
        'TR_XU100': 8500.0, 'EU_STOXX': 4300.0,
        
        # Asia-Pacific
        'JP_NIKKEI': 32500.0, 'JP_TOPIX': 2300.0, 'CN_SSE': 3200.0, 'CN_SZSE': 11000.0,
        'CN_CSI300': 4000.0, 'HK_HSI': 18000.0, 'HK_HSCEI': 6500.0, 'KR_KOSPI': 2650.0,
        'KR_KOSDAQ': 950.0, 'TW_TAIEX': 17000.0, 'IN_SENSEX': 72000.0, 'IN_NIFTY': 21500.0,
        'IN_NIFTY500': 19000.0, 'SG_STI': 3350.0, 'AU_ASX': 7400.0, 'AU_ALL': 7800.0,
        'NZ_NZX': 12000.0, 'TH_SET': 1500.0, 'MY_KLSE': 1500.0, 'ID_JCI': 7200.0,
        'PH_PSE': 6800.0, 'VN_VNI': 1200.0, 'PK_KSE': 65000.0, 'BD_DSE': 6500.0,
        'LK_CSE': 11000.0,
        
        # Latin America
        'BR_IBOV': 130000.0, 'AR_MERV': 1100000.0, 'CL_IPSA': 5500.0, 'CO_COLCAP': 1500.0,
        'PE_SPBLPGPT': 22000.0, 'VE_IBC': 15000.0, 'CR_CRSMBCT': 12000.0, 'JM_JSE': 400000.0,
        
        # Middle East
        'IL_TA125': 1900.0, 'SA_TASI': 11000.0, 'AE_ADX': 9500.0, 'AE_DFM': 4000.0,
        'QA_DSM': 3500.0, 'KW_BKP': 6500.0,
        
        # Africa - Southern
        'ZA_JSE': 65000.0, 'ZA_JALSH': 75000.0, 'BW_BSE': 7800.0, 'ZM_LUSE': 5200.0,
        'ZW_ZSE': 8500.0, 'NA_NSX': 1650.0, 'MZ_BVM': 1200.0, 'MW_MSE': 950.0,
        'AO_BVDA': 2800.0, 'SZ_SSX': 180.0, 'LS_MSM': 95.0,
        # Africa - East
        'KE_NSE': 180.0, 'UG_USE': 2500.0, 'TZ_DSE': 2100.0, 'RW_RSE': 145.0,
        'ET_ESX': 3500.0, 'MU_SEMDEX': 2100.0, 'SO_SSE': 850.0, 'DJ_DSE': 1200.0,
        'ER_ESE': 680.0, 'SC_SSE': 420.0,
        # Africa - North
        'EG_EGX': 25000.0, 'MA_MASI': 13000.0, 'TN_TUNINDEX': 7800.0, 'DZ_DZAIRINDEX': 4200.0,
        'LY_LSM': 3800.0, 'SD_KSE': 2200.0,
        # Africa - West
        'NG_NSE': 72000.0, 'GH_GSE': 3100.0, 'CI_BRVM': 215.0, 'SN_BRVM': 180.0,
        'BJ_BRVM': 165.0, 'CM_DSX': 1650.0, 'NE_NSE': 890.0, 'BF_BRVM': 145.0,
        
        # Additional Europe
        'RO_BET': 13500.0, 'BG_SOFIX': 620.0, 'HR_CROBEX': 2200.0, 'SI_SBITOP': 1150.0,
        'RS_BELEX': 850.0, 'SK_SAX': 380.0, 'LT_OMXV': 1280.0, 'LV_OMXR': 1150.0,
        'EE_OMXT': 1680.0, 'UA_PFTS': 1800.0, 'IS_ICEX': 2450.0, 'LU_LUXX': 1680.0,
        'MT_MSE': 4200.0, 'CY_CSE': 68.0, 'MK_MSE': 2850.0,
        
        # Additional Middle East & Central Asia
        'JO_ASE': 2450.0, 'LB_BLOM': 950.0, 'OM_MSM': 4600.0, 'BH_BAX': 1950.0,
        'PS_PSE': 550.0, 'KZ_KASE': 3200.0, 'UZ_UZSE': 1450.0, 'GE_GSE': 3800.0,
        'AM_AMX': 680.0, 'AZ_AZSE': 1250.0,
        
        # Additional Asia-Pacific
        'MN_MSE': 1650.0, 'KH_CSX': 680.0, 'LA_LSX': 1200.0, 'MM_YSX': 2100.0,
        'NP_NEPSE': 2850.0, 'BT_RSE': 480.0, 'MV_MSE': 850.0, 'BN_BSE': 1580.0,
        'FJ_SPX': 3500.0, 'PG_PNGX': 9500.0, 'MO_MSE': 4200.0, 'TL_TLSE': 650.0,
        
        # Additional Latin America & Caribbean
        'UY_ BOLSA': 1850.0, 'PY_BVPASA': 850.0, 'BO_BOLSA': 12500.0, 'EC_IPEC': 1350.0,
        'PA_BVPAN': 15800.0, 'SV_BVES': 420.0, 'GT_BVG': 1200.0, 'HN_BVH': 480.0,
        'NI_BVDN': 350.0, 'DO_BVRD': 1100.0, 'TT_TTSE': 1650.0, 'BB_BSE': 3200.0,
        'BS_BISX': 2850.0, 'BM_BSX': 1580.0,
    }
    
    @classmethod
    def _generate_mock_data(cls, market_id: str, days_back: int = 30) -> dict:
        """Generate mock data for testing"""
        base_price = cls.MOCK_PRICES.get(market_id, 4500.0)
        
        # Generate price sequence for past 30 days
        prices_30d = []
        current_price = base_price
        for i in range(days_back):
            # Random fluctuation ±2%
            change = random.uniform(-0.02, 0.02)
            current_price = current_price * (1 + change)
            prices_30d.append(round(current_price, 2))
        
        # Latest price and percentage change
        latest_price = prices_30d[-1]
        prev_price = prices_30d[-2] if len(prices_30d) > 1 else prices_30d[-1]
        change_pct = ((latest_price - prev_price) / prev_price) * 100
        
        return {
            'market_id': market_id,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'close_price': round(latest_price, 2),
            'open_price': round(latest_price * 0.995, 2),
            'high_price': round(latest_price * 1.01, 2),
            'low_price': round(latest_price * 0.99, 2),
            'volume': random.randint(1000000, 10000000),
            'change_pct': round(change_pct, 2),
            'prices_30d': prices_30d,
        }
    
    @classmethod
    def fetch_market_data(cls, market_id: str, days_back: int = 30, use_mock: bool = False) -> dict:
        """
        Fetch historical data for a single market
        
        Args:
            market_id: Market ID (e.g., 'US_SPX')
            days_back: Number of days to look back (default 30)
            use_mock: Whether to use mock data
            
        Returns:
            {
                'market_id': 'US_SPX',
                'date': '2026-01-17',
                'close_price': 4500.15,
                'volume': 5000000,
                'change_pct': 1.5,
                'high_price': 4520.50,
                'low_price': 4480.25,
                'open_price': 4430.00,
                'prices_30d': [...]  # Past 30 days close prices for volatility calculation
            }
        """
        try:
            # Return mock data if requested or market ID doesn't exist
            if use_mock or market_id not in cls.MARKET_SYMBOLS:
                if market_id not in cls.MARKET_SYMBOLS:
                    logger.error(f"Unknown market ID: {market_id}")
                    return None
                return cls._generate_mock_data(market_id, days_back)
            
            symbol = cls.MARKET_SYMBOLS.get(market_id)
            if not symbol:
                logger.error(f"Unknown market ID: {market_id}")
                return None
            
            # Fetch data
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Download historical data
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                logger.warning(f"No data found for {market_id} ({symbol}), using mock data")
                return cls._generate_mock_data(market_id, days_back)
            
            # Get the latest row
            latest = hist.iloc[-1]
            
            # Calculate percentage change
            if len(hist) > 1:
                prev_close = hist.iloc[-2]['Close']
                change_pct = ((latest['Close'] - prev_close) / prev_close) * 100
            else:
                change_pct = 0.0
            
            # Construct return data
            result = {
                'market_id': market_id,
                'date': end_date.strftime('%Y-%m-%d'),
                'close_price': float(latest['Close']),
                'open_price': float(latest['Open']),
                'high_price': float(latest['High']),
                'low_price': float(latest['Low']),
                'volume': int(latest['Volume']) if latest['Volume'] > 0 else 0,
                'change_pct': round(change_pct, 2),
                'prices_30d': hist['Close'].tolist(),  # Past 30 days close prices
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"Error fetching data for {market_id}: {str(e)}, using mock data")
            return cls._generate_mock_data(market_id, days_back)
    
    @classmethod
    def fetch_multiple_markets(cls, market_ids: list, days_back: int = 30, use_mock: bool = False) -> dict:
        """
        Batch fetch data for multiple markets
        
        Returns:
            {
                'success': ['US_SPX', 'EU_STOXX', ...],
                'failed': ['UNKNOWN_ID', ...],
                'data': {
                    'US_SPX': {...},
                    'EU_STOXX': {...},
                    ...
                }
            }
        """
        result = {
            'success': [],
            'failed': [],
            'data': {}
        }
        
        for market_id in market_ids:
            data = cls.fetch_market_data(market_id, days_back, use_mock=use_mock)
            if data:
                result['success'].append(market_id)
                result['data'][market_id] = data
            else:
                result['failed'].append(market_id)
        
        return result
    
    @classmethod
    def fetch_default_markets(cls, days_back: int = 30, use_mock: bool = False) -> dict:
        """
        Fetch data for all main markets (all currently supported markets)
        """
        return cls.fetch_multiple_markets(list(cls.MARKET_SYMBOLS.keys()), days_back, use_mock=use_mock)
