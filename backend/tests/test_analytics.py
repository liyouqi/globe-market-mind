"""
Unit tests for Analytics Engine
Test feature calculation, mood index, and correlation calculation
"""

import sys
import os

# Add backend to path (works from any location)
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

from app.services.analytics import (
    FeatureCalculator, MoodEngine, CorrelationCalculator, AnalyticsEngine
)


def test_feature_calculator():
    """Test Phase 1: Feature calculation"""
    print("\n" + "="*60)
    print("TEST 1: Feature Calculator (Phase 1)")
    print("="*60)
    
    # Test return calculation
    return_val = FeatureCalculator.calculate_return_today(4535.62, 4510.0)
    print(f"Daily Return (4535.62 from 4510.0): {return_val:.4f}%")
    assert abs(return_val - 0.569) < 0.01, "Return calculation failed"
    
    # Test volatility calculation with sample data
    prices_30d = [4400, 4420, 4410, 4450, 4500, 4510, 4535, 4520, 4550, 4500,
                  4480, 4510, 4530, 4515, 4545, 4560, 4530, 4500, 4520, 4540,
                  4510, 4530, 4550, 4560, 4540, 4520, 4535, 4562, 4550, 4535]
    volatility = FeatureCalculator.calculate_volatility_30d(prices_30d)
    print(f"30-Day Volatility (30 prices): {volatility:.4f}%")
    assert volatility > 0, "Volatility should be positive"
    
    # Test volume score
    volume_score = FeatureCalculator.calculate_volume_score(
        current_volume=450000000,
        prices_30d=prices_30d
    )
    print(f"Volume Score: {volume_score:.4f}")
    
    # Test Z-score normalization
    z_score = FeatureCalculator.z_score_normalize(0.569, 0, 2.0)
    print(f"Z-Score of 0.569% (μ=0, σ=2): {z_score:.4f}")
    
    # Extract complete features
    market_data = {
        'close_price': 4535.62,
        'volume': 450000000,
        'prices_30d': prices_30d
    }
    features = FeatureCalculator.extract_features(market_data)
    print(f"\nExtracted Features:")
    print(f"  Return Today: {features['return_today']:.4f}%")
    print(f"  Volatility 30D: {features['volatility_30d']:.4f}%")
    print(f"  Volume Score: {features['volume_score']:.4f}")
    print(f"  Return Normalized: {features['return_normalized']:.4f}")
    print(f"  Volatility Normalized: {features['volatility_normalized']:.4f}")
    print(f"  Volume Normalized: {features['volume_normalized']:.4f}")
    
    print("\n✓ Phase 1 Tests PASSED")
    return features


def test_mood_engine(features):
    """Test Phase 2: Mood index calculation"""
    print("\n" + "="*60)
    print("TEST 2: Mood Engine (Phase 2)")
    print("="*60)
    
    # Test mood index calculation
    mood_index = MoodEngine.calculate_mood_index(features)
    print(f"Calculated Mood Index: {mood_index:.4f}")
    assert -1.0 <= mood_index <= 1.0, "Mood index out of range"
    
    # Test mood level conversion
    mood_levels = [
        (-0.9, 'very_bearish'),
        (-0.3, 'bearish'),
        (0.0, 'neutral'),
        (0.3, 'bullish'),
        (0.8, 'very_bullish'),
    ]
    
    print("\nMood Level Mapping:")
    for mood_val, expected_level in mood_levels:
        level = MoodEngine.mood_to_level(mood_val)
        print(f"  {mood_val:>5.1f} → {level:>15} {'✓' if level == expected_level else '✗'}")
        assert level == expected_level, f"Expected {expected_level}, got {level}"
    
    # Test complete mood calculation
    market_data = {
        'close_price': 4535.62,
        'volume': 450000000,
        'prices_30d': [4400, 4420, 4410, 4450, 4500, 4510, 4535, 4520, 4550, 4500,
                      4480, 4510, 4530, 4515, 4545, 4560, 4530, 4500, 4520, 4540,
                      4510, 4530, 4550, 4560, 4540, 4520, 4535, 4562, 4550, 4535]
    }
    mood_result = MoodEngine.calculate_mood(market_data)
    print(f"\nComplete Mood Calculation:")
    print(f"  Mood Index: {mood_result['mood_index']:.4f}")
    print(f"  Mood Level: {mood_result['mood_level']}")
    
    print("\n✓ Phase 2 Tests PASSED")
    return mood_result


def test_correlation_calculator():
    """Test Phase 3: Correlation calculation"""
    print("\n" + "="*60)
    print("TEST 3: Correlation Calculator (Phase 3)")
    print("="*60)
    
    # Create test data for multiple markets
    prices_us = [4400, 4420, 4410, 4450, 4500, 4510, 4535, 4520, 4550, 4500,
                 4480, 4510, 4530, 4515, 4545, 4560, 4530, 4500, 4520, 4540,
                 4510, 4530, 4550, 4560, 4540, 4520, 4535, 4562, 4550, 4535]
    
    # EU prices (correlated with US: ~0.7)
    prices_eu = [3900, 3920, 3910, 3950, 4000, 4010, 4035, 4020, 4050, 4000,
                 3980, 4010, 4030, 4015, 4045, 4060, 4030, 4000, 4020, 4040,
                 4010, 4030, 4050, 4060, 4040, 4020, 4035, 4062, 4050, 4035]
    
    # Asia prices (negatively correlated: ~-0.3)
    prices_asia = [31000, 31100, 31050, 30950, 30900, 30800, 30700, 30650, 30600, 30700,
                   30800, 30900, 31000, 31100, 31050, 30950, 31150, 31250, 31100, 31000,
                   31050, 30950, 30850, 30750, 30900, 31050, 31100, 31000, 31150, 31250]
    
    # Test returns extraction
    returns_us = CorrelationCalculator.extract_returns(prices_us)
    print(f"US Returns Series: {len(returns_us)} daily returns")
    print(f"  First 5: {[f'{r:.2f}%' for r in returns_us[:5]]}")
    
    # Test Pearson correlation
    corr_us_eu = CorrelationCalculator.calculate_pearson_correlation(returns_us, 
                                                                     CorrelationCalculator.extract_returns(prices_eu))
    print(f"\nCorrelation US-EU: {corr_us_eu:.4f}")
    
    corr_us_asia = CorrelationCalculator.calculate_pearson_correlation(returns_us,
                                                                       CorrelationCalculator.extract_returns(prices_asia))
    print(f"Correlation US-Asia: {corr_us_asia:.4f}")
    
    # Test batch correlation calculation
    markets_data = {
        'US_SPX': {'prices_30d': prices_us},
        'EU_STOXX': {'prices_30d': prices_eu},
        'JP_NIKKEI': {'prices_30d': prices_asia},
    }
    
    correlations = CorrelationCalculator.calculate_correlations(markets_data)
    print(f"\nCorrelation Network Edges (threshold > 0.6):")
    for edge in correlations['edges']:
        print(f"  {edge['source']} ↔ {edge['target']}: {edge['weight']:.4f} ({edge['type']})")
    
    print("\n✓ Phase 3 Tests PASSED")


def test_analytics_engine():
    """Test complete Analytics Engine"""
    print("\n" + "="*60)
    print("TEST 4: Complete Analytics Engine")
    print("="*60)
    
    # Sample market data
    market_data = {
        'US_SPX': {
            'market_id': 'US_SPX',
            'close_price': 4535.62,
            'volume': 450000000,
            'prices_30d': [4400, 4420, 4410, 4450, 4500, 4510, 4535, 4520, 4550, 4500,
                          4480, 4510, 4530, 4515, 4545, 4560, 4530, 4500, 4520, 4540,
                          4510, 4530, 4550, 4560, 4540, 4520, 4535, 4562, 4550, 4535]
        },
        'EU_STOXX': {
            'market_id': 'EU_STOXX',
            'close_price': 3965.10,
            'volume': 250000000,
            'prices_30d': [3900, 3920, 3910, 3950, 4000, 4010, 4035, 4020, 4050, 4000,
                          3980, 4010, 4030, 4015, 4045, 4060, 4030, 4000, 4020, 4040,
                          4010, 4030, 4050, 4060, 4040, 4020, 4035, 4062, 4050, 3965]
        },
        'JP_NIKKEI': {
            'market_id': 'JP_NIKKEI',
            'close_price': 31816.13,
            'volume': 350000000,
            'prices_30d': [31000, 31100, 31050, 30950, 30900, 30800, 30700, 30650, 30600, 30700,
                          30800, 30900, 31000, 31100, 31050, 30950, 31150, 31250, 31100, 31000,
                          31050, 30950, 30850, 30750, 30900, 31050, 31100, 31000, 31150, 31816]
        }
    }
    
    # Test single market analytics
    print("\nSingle Market Analytics:")
    analytics_us = AnalyticsEngine.calculate_market_analytics(market_data['US_SPX'])
    print(f"US_SPX:")
    print(f"  Mood Index: {analytics_us['mood_index']:.4f}")
    print(f"  Mood Level: {analytics_us['mood_level']}")
    print(f"  Volatility 30D: {analytics_us['volatility_30d']:.4f}%")
    print(f"  Trend Strength: {analytics_us['trend_strength']:.4f}")
    
    # Test batch processing
    print("\nBatch Market Analytics:")
    results = AnalyticsEngine.process_market_batch(market_data)
    print(f"Processing Date: {results['date']}")
    print(f"Markets Processed: {len(results['markets'])}")
    
    for market_id, analytics in results['markets'].items():
        if analytics:
            print(f"\n{market_id}:")
            print(f"  Mood: {analytics['mood_index']:.4f} ({analytics['mood_level']})")
            print(f"  Volatility: {analytics['volatility_30d']:.4f}%")
    
    print(f"\nCorrelation Edges Found: {len(results['correlations']['edges'])}")
    for edge in results['correlations']['edges'][:3]:
        print(f"  {edge['source']} ↔ {edge['target']}: {edge['weight']:.4f}")
    
    print("\n✓ Analytics Engine Tests PASSED")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("ANALYTICS ENGINE TEST SUITE")
    print("="*60)
    
    try:
        # Run Phase 1 tests
        features = test_feature_calculator()
        
        # Run Phase 2 tests
        mood_result = test_mood_engine(features)
        
        # Run Phase 3 tests
        test_correlation_calculator()
        
        # Run complete engine tests
        test_analytics_engine()
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED ✓")
        print("="*60)
        print("\nAnalytics Engine is ready for integration")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
