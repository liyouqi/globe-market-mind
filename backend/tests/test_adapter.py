"""
Test Adapter Service
"""

import sys
import os

# Add backend to path (works from any location)
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

from app.services.adapter import YahooFinanceAdapter
import json

if __name__ == '__main__':
    # Test single market (using mock data)
    print("=" * 60)
    print("Test single market: US_SPX (S&P 500)")
    print("=" * 60)
    
    data = YahooFinanceAdapter.fetch_market_data('US_SPX', use_mock=True)
    if data:
        print(json.dumps({
            'market_id': data['market_id'],
            'date': data['date'],
            'close_price': data['close_price'],
            'change_pct': data['change_pct'],
            'volume': data['volume'],
            'prices_30d_count': len(data['prices_30d']),
        }, indent=2))
    else:
        print("Failed to fetch!")
    
    print("\n")
    
    # Test multiple markets
    print("=" * 60)
    print("Test 5 main markets (using mock data)")
    print("=" * 60)
    
    markets = ['US_SPX', 'EU_STOXX', 'JP_NIKKEI', 'CN_SSE', 'IN_SENSEX']
    result = YahooFinanceAdapter.fetch_multiple_markets(markets, use_mock=True)
    
    print(f"Success: {result['success']}")
    print(f"Failed: {result['failed']}")
    print(f"\nData samples:")
    for market_id in result['success'][:3]:
        data = result['data'][market_id]
        print(f"\n{market_id}:")
        print(f"  Date: {data['date']}")
        print(f"  Close Price: {data['close_price']}")
        print(f"  Volume: {data['volume']}")
        print(f"  Change: {data['change_pct']}%")
