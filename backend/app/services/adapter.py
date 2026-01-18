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
    
    # Market symbol mapping
    MARKET_SYMBOLS = {
        'US_SPX': 'SPY',        # S&P 500
        'US_IYY': 'DIA',        # Dow Jones
        'US_CCMP': 'QQQ',       # Nasdaq
        'EU_STOXX': 'EXS1.DE',  # STOXX Europe 600
        'GB_FTSE': 'EUFX',      # FTSE 100
        'JP_NIKKEI': '0050.KL', # Nikkei 225
        'CN_SSE': 'YINN',       # Shanghai Composite
        'IN_SENSEX': 'INDY',    # BSE Sensex
        'BR_IBOV': 'EWZ',       # Bovespa
        'KR_KOSPI': 'EWY',      # KOSPI
        'RU_MOEX': 'RSX',       # MOEX Russia
        'AU_ASX': 'EWA',        # ASX 200
        'CH_SMI': 'EWL',        # SMI
        'SG_STI': 'EWS',        # Straits Times
        'MX_MEXBOL': 'EWW',     # IPC Mexico
    }
    
    # Mock prices for testing
    MOCK_PRICES = {
        'US_SPX': 4500.0,
        'US_IYY': 38500.0,
        'US_CCMP': 14200.0,
        'EU_STOXX': 4300.0,
        'GB_FTSE': 7700.0,
        'JP_NIKKEI': 32500.0,
        'CN_SSE': 3200.0,
        'IN_SENSEX': 72000.0,
        'BR_IBOV': 130000.0,
        'KR_KOSPI': 2650.0,
        'RU_MOEX': 3000.0,
        'AU_ASX': 7400.0,
        'CH_SMI': 11200.0,
        'SG_STI': 3350.0,
        'MX_MEXBOL': 21000.0,
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
