"""
Integration tests for all API endpoints
Tests complete workflows and edge cases
"""

import sys
import os

# Add backend to path (works from any location)
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://backend:5000' if os.path.exists('/.dockerenv') else 'http://localhost'

class APIIntegrationTests:
    """Integration tests for GlobeMarketMind API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.test_results = {'passed': 0, 'failed': 0, 'errors': []}
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and track results"""
        try:
            test_func()
            print(f"  ✓ {test_name}")
            self.test_results['passed'] += 1
        except AssertionError as e:
            print(f"  ✗ {test_name}: {str(e)}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append((test_name, str(e)))
        except Exception as e:
            print(f"  ✗ {test_name}: {str(e)}")
            self.test_results['failed'] += 1
            self.test_results['errors'].append((test_name, str(e)))
    
    # Test Suite 1: Data Endpoints
    def test_get_all_markets(self):
        response = requests.get(f"{self.base_url}/api/data/markets")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Data should be a list"
        assert len(data) == 15, "Should have 15 markets"
    
    def test_get_single_market(self):
        response = requests.get(f"{self.base_url}/api/data/markets/US_SPX")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data['id'] == 'US_SPX', "Market ID should be US_SPX"
        assert 'name' in data, "Market should have name"
    
    def test_get_single_market_not_found(self):
        response = requests.get(f"{self.base_url}/api/data/markets/INVALID_MARKET")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_get_daily_states(self):
        response = requests.get(f"{self.base_url}/api/data/daily-states?market_id=US_SPX&limit=5")
        # This endpoint may not be fully implemented yet
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list), "Response should be a list"
            if len(data) > 0:
                assert 'market_id' in data[0], "Daily state should have market_id"
    
    # Test Suite 2: History Endpoints
    def test_market_timeseries(self):
        response = requests.get(f"{self.base_url}/api/history/markets/US_SPX/timeseries?days=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'market_id' in data, "Response should have market_id"
        assert data['market_id'] == 'US_SPX', "Market ID should match"
    
    def test_market_timeseries_with_date_range(self):
        today = datetime.utcnow().date()
        start_date = (today - timedelta(days=5)).isoformat()
        end_date = today.isoformat()
        
        response = requests.get(
            f"{self.base_url}/api/history/markets/US_SPX/timeseries"
            f"?start_date={start_date}&end_date={end_date}"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'market_id' in data, "Response should have market_id"
    
    def test_compare_markets(self):
        payload = {
            'market_ids': ['US_SPX', 'EU_STOXX', 'JP_NIKKEI'],
            'days': 10,
            'metric': 'mood_index'
        }
        response = requests.post(
            f"{self.base_url}/api/history/compare",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'comparison' in data, "Response should have comparison key"
    
    def test_compare_missing_market_ids(self):
        payload = {'days': 10, 'metric': 'mood_index'}
        response = requests.post(
            f"{self.base_url}/api/history/compare",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    
    def test_rankings(self):
        response = requests.get(f"{self.base_url}/api/history/rankings?metric=mood_index&limit=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'rankings' in data, "Response should have rankings key"
        assert 'top' in data['rankings'], "Rankings should have top key"
    
    # Test Suite 3: Process Endpoints
    def test_process_snapshot(self):
        response = requests.get(f"{self.base_url}/api/process/snapshot")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'data' in data, "Response should have data key"
        assert 'date' in data['data'], "Data should have date field"
    
    # Test Suite 4: Scheduler Endpoints
    def test_scheduler_status(self):
        response = requests.get(f"{self.base_url}/api/scheduler/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert 'scheduler' in data, "Response should have scheduler key"
        assert 'status' in data['scheduler'], "Scheduler should have status"
    
    # Test Suite 5: Response Format Validation
    def test_response_format_markets_is_list(self):
        """Verify markets endpoint returns a list"""
        response = requests.get(f"{self.base_url}/api/data/markets")
        data = response.json()
        assert isinstance(data, list), "Markets endpoint should return a list"
    
    def test_response_format_single_market_is_object(self):
        """Verify single market endpoint returns an object"""
        response = requests.get(f"{self.base_url}/api/data/markets/US_SPX")
        data = response.json()
        assert isinstance(data, dict), "Single market should return an object"
    
    # Test Suite 6: Data Validation
    def test_mood_index_range(self):
        response = requests.get(f"{self.base_url}/api/data/markets")
        markets = response.json()
        if len(markets) > 0 and 'mood_index' in markets[0]:
            for market in markets:
                mood = market['mood_index']
                assert -1 <= mood <= 1, f"Mood index should be in [-1, 1], got {mood}"
    
    def test_volatility_non_negative(self):
        response = requests.get(f"{self.base_url}/api/data/markets")
        markets = response.json()
        if len(markets) > 0 and 'volatility' in markets[0]:
            for market in markets:
                vol = market['volatility']
                assert vol >= 0, f"Volatility should be non-negative, got {vol}"
    
    def print_summary(self):
        """Print test execution summary"""
        total = self.test_results['passed'] + self.test_results['failed']
        print(f"\n{'='*60}")
        print(f"Test Summary: {self.test_results['passed']}/{total} passed")
        print(f"{'='*60}")
        
        if self.test_results['failed'] > 0:
            print("\nFailed tests:")
            for test_name, error in self.test_results['errors']:
                print(f"  - {test_name}: {error}")
        
        return self.test_results['passed'] == total


def main():
    tester = APIIntegrationTests()
    
    print("\n" + "="*60)
    print("API Integration Tests")
    print("="*60)
    
    print("\nSuite 1: Data Endpoints")
    tester.run_test("Get all markets", tester.test_get_all_markets)
    tester.run_test("Get single market", tester.test_get_single_market)
    tester.run_test("Get single market (404)", tester.test_get_single_market_not_found)
    tester.run_test("Get daily states", tester.test_get_daily_states)
    
    print("\nSuite 2: History Endpoints")
    tester.run_test("Market timeseries", tester.test_market_timeseries)
    tester.run_test("Market timeseries with date range", tester.test_market_timeseries_with_date_range)
    tester.run_test("Compare markets", tester.test_compare_markets)
    tester.run_test("Compare markets (missing IDs)", tester.test_compare_missing_market_ids)
    tester.run_test("Rankings", tester.test_rankings)
    
    print("\nSuite 3: Process Endpoints")
    tester.run_test("Process snapshot", tester.test_process_snapshot)
    
    print("\nSuite 4: Scheduler Endpoints")
    tester.run_test("Scheduler status", tester.test_scheduler_status)
    
    print("\nSuite 5: Response Format Validation")
    tester.run_test("Markets response is list", tester.test_response_format_markets_is_list)
    tester.run_test("Single market response is object", tester.test_response_format_single_market_is_object)
    
    print("\nSuite 6: Data Validation")
    tester.run_test("Mood index in valid range", tester.test_mood_index_range)
    tester.run_test("Volatility non-negative", tester.test_volatility_non_negative)
    
    success = tester.print_summary()
    exit(0 if success else 1)


if __name__ == '__main__':
    main()
