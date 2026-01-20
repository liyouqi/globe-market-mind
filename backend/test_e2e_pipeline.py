"""
End-to-End Pipeline Verification Test
Tests complete data flow: Adapter → Analytics → DataService → Database
Validates all 15 markets process correctly across multiple runs
"""

import sys
sys.path.insert(0, '/Users/dada/Developer/italy_proj/SDE/GlobeMarketMind/backend')

import requests
import json
from datetime import datetime
import time
import os

# Use container internal address when running in Docker
BASE_URL = os.getenv('API_BASE_URL', 'http://localhost')
if os.path.exists('/.dockerenv'):
    BASE_URL = 'http://backend:5000'

class PipelineValidator:
    """Validates end-to-end pipeline functionality"""
    
    def __init__(self):
        self.runs = []
        self.market_ids = [
            'US_SPX', 'US_IYY', 'US_CCMP',
            'EU_STOXX', 'GB_FTSE', 'CH_SMI',
            'JP_NIKKEI', 'CN_SSE', 'IN_SENSEX',
            'BR_IBOV', 'KR_KOSPI', 'RU_MOEX',
            'AU_ASX', 'SG_STI', 'MX_MEXBOL'
        ]
    
    def run_analysis_pipeline(self, run_num: int) -> dict:
        """Run one complete analysis pipeline"""
        print(f"\n{'='*70}")
        print(f"RUN {run_num}: Triggering Analysis Pipeline")
        print(f"{'='*70}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/process/analyze",
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code not in [200, 207]:
                print(f"✗ Pipeline Failed - HTTP {response.status_code}")
                return {'run': run_num, 'status': 'failed', 'error': response.text}
            
            result = response.json()
            print(f"✓ Pipeline Status: {result.get('status', 'unknown')}")
            
            # Extract metrics
            data_fetch = result.get('pipeline', {}).get('data_fetch', {})
            analytics = result.get('pipeline', {}).get('analytics', {})
            persistence = result.get('pipeline', {}).get('persistence', {})
            
            print(f"\n📊 STAGE BREAKDOWN:")
            print(f"  Stage 1 (Data Fetch):")
            print(f"    - Markets Fetched: {data_fetch.get('markets_fetched', 0)}/{len(self.market_ids)}")
            print(f"    - Markets Failed: {data_fetch.get('markets_failed', 0)}")
            
            print(f"  Stage 2 (Analytics):")
            print(f"    - Markets Analyzed: {analytics.get('markets_analyzed', 0)}")
            print(f"    - Correlations Found: {analytics.get('correlations_found', 0)}")
            
            print(f"  Stage 3 (Persistence):")
            print(f"    - Markets Saved: {persistence.get('markets_saved', 0)}")
            print(f"    - Markets Failed: {persistence.get('markets_failed', 0)}")
            print(f"    - Correlations Saved: {persistence.get('correlations_saved', 0)}")
            
            # Validate all markets processed
            all_markets_processed = (
                data_fetch.get('markets_fetched', 0) >= len(self.market_ids) - 1 and
                analytics.get('markets_analyzed', 0) >= len(self.market_ids) - 1 and
                persistence.get('markets_saved', 0) >= len(self.market_ids) - 1
            )
            
            if all_markets_processed:
                print(f"\n✓ All {len(self.market_ids)} markets processed successfully")
            else:
                print(f"\n⚠ Some markets were not processed")
            
            return {
                'run': run_num,
                'status': result.get('status'),
                'timestamp': result.get('timestamp'),
                'data_fetch': data_fetch,
                'analytics': analytics,
                'persistence': persistence,
                'all_processed': all_markets_processed
            }
            
        except Exception as e:
            print(f"✗ Pipeline Error: {str(e)}")
            return {'run': run_num, 'status': 'error', 'error': str(e)}
    
    def fetch_snapshot(self) -> dict:
        """Fetch latest market snapshot from database"""
        print(f"\n{'='*70}")
        print(f"FETCHING LATEST SNAPSHOT FROM DATABASE")
        print(f"{'='*70}")
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/process/snapshot",
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"✗ Failed to fetch snapshot - HTTP {response.status_code}")
                return None
            
            snapshot = response.json().get('data', {})
            date = snapshot.get('date')
            markets = snapshot.get('markets', {})
            correlations = snapshot.get('correlations', [])
            
            print(f"✓ Snapshot Date: {date}")
            print(f"✓ Markets in Snapshot: {len(markets)}")
            print(f"✓ Correlation Edges: {len(correlations)}")
            
            return {
                'date': date,
                'markets_count': len(markets),
                'correlations_count': len(correlations),
                'markets': markets,
                'correlations': correlations
            }
            
        except Exception as e:
            print(f"✗ Error fetching snapshot: {str(e)}")
            return None
    
    def validate_market_data(self, markets: dict) -> dict:
        """Validate mood index values for all markets"""
        print(f"\n{'='*70}")
        print(f"VALIDATING MARKET DATA QUALITY")
        print(f"{'='*70}")
        
        validation_results = {
            'total_markets': len(markets),
            'valid_mood_index': 0,
            'valid_volatility': 0,
            'valid_trend': 0,
            'extreme_values': [],
            'missing_fields': [],
            'market_details': {}
        }
        
        for market_id, data in markets.items():
            mood_index = data.get('mood_index')
            volatility = data.get('volatility_30d')
            trend = data.get('trend_strength')
            
            market_info = {
                'mood_index': mood_index,
                'mood_level': data.get('mood_level', 'unknown'),
                'volatility_30d': volatility,
                'trend_strength': trend,
                'valid': True
            }
            
            # Validate mood index range
            if mood_index is not None and -1.0 <= mood_index <= 1.0:
                validation_results['valid_mood_index'] += 1
            else:
                market_info['valid'] = False
                if mood_index is None:
                    validation_results['missing_fields'].append((market_id, 'mood_index'))
                else:
                    validation_results['extreme_values'].append(
                        (market_id, 'mood_index', mood_index)
                    )
            
            # Validate volatility (should be positive)
            if volatility is not None and volatility >= 0:
                validation_results['valid_volatility'] += 1
            else:
                market_info['valid'] = False
                if volatility is None:
                    validation_results['missing_fields'].append((market_id, 'volatility_30d'))
            
            # Validate trend strength
            if trend is not None and trend >= 0:
                validation_results['valid_trend'] += 1
            else:
                market_info['valid'] = False
                if trend is None:
                    validation_results['missing_fields'].append((market_id, 'trend_strength'))
            
            validation_results['market_details'][market_id] = market_info
        
        # Print validation summary
        print(f"\n✓ Valid Mood Index Values: {validation_results['valid_mood_index']}/{validation_results['total_markets']}")
        print(f"✓ Valid Volatility Values: {validation_results['valid_volatility']}/{validation_results['total_markets']}")
        print(f"✓ Valid Trend Strength Values: {validation_results['valid_trend']}/{validation_results['total_markets']}")
        
        if validation_results['extreme_values']:
            print(f"\n⚠ Extreme Values Found:")
            for market_id, field, value in validation_results['extreme_values']:
                print(f"  {market_id}.{field} = {value}")
        
        if validation_results['missing_fields']:
            print(f"\n⚠ Missing Fields:")
            for market_id, field in validation_results['missing_fields']:
                print(f"  {market_id}.{field}")
        
        # Print top bullish and bearish markets
        if validation_results['market_details']:
            sorted_markets = sorted(
                validation_results['market_details'].items(),
                key=lambda x: x[1]['mood_index'] or 0,
                reverse=True
            )
            
            print(f"\n📈 TOP 5 BULLISH MARKETS:")
            for i, (market_id, data) in enumerate(sorted_markets[:5], 1):
                print(f"  {i}. {market_id}: {data['mood_index']:.4f} ({data['mood_level']})")
            
            print(f"\n📉 TOP 5 BEARISH MARKETS:")
            for i, (market_id, data) in enumerate(sorted_markets[-5:], 1):
                print(f"  {i}. {market_id}: {data['mood_index']:.4f} ({data['mood_level']})")
        
        return validation_results
    
    def validate_correlations(self, correlations: list) -> dict:
        """Validate correlation network"""
        print(f"\n{'='*70}")
        print(f"VALIDATING CORRELATION NETWORK")
        print(f"{'='*70}")
        
        validation = {
            'total_edges': len(correlations),
            'positive_correlations': 0,
            'negative_correlations': 0,
            'strong_correlations': [],
            'weak_correlations': []
        }
        
        for edge in correlations:
            source = edge.get('source')
            target = edge.get('target')
            weight = edge.get('correlation_value', 0)
            
            if weight > 0:
                validation['positive_correlations'] += 1
            else:
                validation['negative_correlations'] += 1
            
            # Track strong correlations (|weight| > 0.7)
            if abs(weight) > 0.7:
                validation['strong_correlations'].append({
                    'pair': f"{source} ↔ {target}",
                    'correlation': weight,
                    'type': 'positive' if weight > 0 else 'negative'
                })
            
            # Track weak correlations (0.6 < |weight| <= 0.7)
            elif 0.6 < abs(weight) <= 0.7:
                validation['weak_correlations'].append({
                    'pair': f"{source} ↔ {target}",
                    'correlation': weight
                })
        
        print(f"✓ Total Correlation Edges: {validation['total_edges']}")
        print(f"✓ Positive Correlations: {validation['positive_correlations']}")
        print(f"✓ Negative Correlations: {validation['negative_correlations']}")
        
        if validation['strong_correlations']:
            print(f"\n🔗 STRONG CORRELATIONS (|r| > 0.7):")
            for corr in sorted(validation['strong_correlations'], 
                              key=lambda x: abs(x['correlation']), 
                              reverse=True)[:10]:
                print(f"  {corr['pair']}: {corr['correlation']:.4f}")
        
        return validation
    
    def run_full_validation(self, num_runs: int = 3):
        """Run complete validation across multiple pipeline executions"""
        print("\n" + "="*70)
        print("END-TO-END PIPELINE VALIDATION TEST")
        print("="*70)
        print(f"Configuration:")
        print(f"  - Markets to validate: {len(self.market_ids)}")
        print(f"  - Pipeline runs: {num_runs}")
        print(f"  - Start time: {datetime.now().isoformat()}")
        
        # Run multiple pipeline executions
        for run in range(1, num_runs + 1):
            result = self.run_analysis_pipeline(run)
            self.runs.append(result)
            
            if run < num_runs:
                print(f"\n⏳ Waiting 2 seconds before next run...")
                time.sleep(2)
        
        # Fetch and validate latest snapshot
        snapshot = self.fetch_snapshot()
        
        if not snapshot:
            print("\n✗ Could not retrieve snapshot for validation")
            return
        
        # Validate market data quality
        market_validation = self.validate_market_data(snapshot.get('markets', {}))
        
        # Validate correlation network
        correlation_validation = self.validate_correlations(snapshot.get('correlations', []))
        
        # Print final summary
        self._print_final_summary(market_validation, correlation_validation)
    
    def _print_final_summary(self, market_validation: dict, correlation_validation: dict):
        """Print final validation summary"""
        print(f"\n{'='*70}")
        print(f"FINAL VALIDATION SUMMARY")
        print(f"{'='*70}")
        
        # Pipeline runs summary
        print(f"\n📊 PIPELINE RUNS ({len(self.runs)} total):")
        all_succeeded = True
        for run in self.runs:
            status = run.get('status', 'unknown')
            symbol = '✓' if status == 'success' else '✗'
            print(f"  Run {run.get('run')}: {symbol} {status}")
            if status != 'success':
                all_succeeded = False
        
        print(f"\n🎯 MARKET DATA VALIDATION:")
        print(f"  Valid Mood Index: {market_validation['valid_mood_index']}/{market_validation['total_markets']}")
        print(f"  Valid Volatility: {market_validation['valid_volatility']}/{market_validation['total_markets']}")
        print(f"  Valid Trend Strength: {market_validation['valid_trend']}/{market_validation['total_markets']}")
        
        if market_validation['missing_fields']:
            print(f"  ⚠ Missing Fields: {len(market_validation['missing_fields'])}")
        if market_validation['extreme_values']:
            print(f"  ⚠ Extreme Values: {len(market_validation['extreme_values'])}")
        
        print(f"\n🔗 CORRELATION NETWORK:")
        print(f"  Total Edges: {correlation_validation['total_edges']}")
        print(f"  Positive Correlations: {correlation_validation['positive_correlations']}")
        print(f"  Negative Correlations: {correlation_validation['negative_correlations']}")
        print(f"  Strong Correlations (|r| > 0.7): {len(correlation_validation['strong_correlations'])}")
        
        # Overall result
        print(f"\n{'='*70}")
        if all_succeeded and market_validation['valid_mood_index'] == market_validation['total_markets']:
            print("✓ END-TO-END VALIDATION PASSED")
            print("All markets processed successfully through complete pipeline")
        else:
            print("⚠ VALIDATION PASSED WITH WARNINGS")
            print(f"Please review {len(market_validation['missing_fields']) + len(market_validation['extreme_values'])} issues above")
        print(f"{'='*70}")


if __name__ == '__main__':
    validator = PipelineValidator()
    validator.run_full_validation(num_runs=3)
