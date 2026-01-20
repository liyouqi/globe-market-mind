"""
Performance benchmark tests
Tests API response times and throughput under load
"""

import sys
import os

# Add backend to path (works from any location)
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_path)

import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

# Use container internal address when running in Docker
BASE_URL = 'http://backend:5000' if os.path.exists('/.dockerenv') else 'http://localhost'

class PerformanceTester:
    """Performance testing utilities"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = {}
    
    def test_endpoint(self, name: str, method: str, path: str, 
                      payload: dict = None, iterations: int = 10) -> dict:
        """
        Test an endpoint multiple times and collect metrics
        
        Returns:
            {
                'name': 'Test name',
                'total_time': 1.234,
                'iterations': 10,
                'min_ms': 45.2,
                'max_ms': 120.5,
                'avg_ms': 78.3,
                'median_ms': 75.0,
                'p95_ms': 115.0,
                'success': 10,
                'failed': 0
            }
        """
        times = []
        successes = 0
        failures = 0
        
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print(f"{'='*60}")
        print(f"Endpoint: {method} {path}")
        print(f"Iterations: {iterations}")
        
        start_total = time.time()
        
        for i in range(iterations):
            try:
                start = time.time()
                
                if method.upper() == 'GET':
                    response = requests.get(
                        f"{self.base_url}{path}",
                        timeout=10
                    )
                elif method.upper() == 'POST':
                    response = requests.post(
                        f"{self.base_url}{path}",
                        json=payload,
                        timeout=10,
                        headers={'Content-Type': 'application/json'}
                    )
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                elapsed = (time.time() - start) * 1000  # Convert to ms
                times.append(elapsed)
                
                if response.status_code < 400:
                    successes += 1
                    status = '✓'
                else:
                    failures += 1
                    status = '✗'
                
                print(f"  [{i+1}/{iterations}] {status} {response.status_code} - {elapsed:.1f}ms")
                
            except Exception as e:
                failures += 1
                print(f"  [{i+1}/{iterations}] ✗ ERROR - {str(e)}")
        
        total_time = time.time() - start_total
        
        if times:
            result = {
                'name': name,
                'endpoint': f"{method} {path}",
                'total_time': round(total_time, 3),
                'iterations': iterations,
                'min_ms': round(min(times), 2),
                'max_ms': round(max(times), 2),
                'avg_ms': round(statistics.mean(times), 2),
                'median_ms': round(statistics.median(times), 2),
                'p95_ms': round(sorted(times)[int(len(times)*0.95)], 2),
                'success': successes,
                'failed': failures,
                'throughput': round(iterations / total_time, 2)  # requests/sec
            }
        else:
            result = {
                'name': name,
                'endpoint': f"{method} {path}",
                'error': 'No successful requests',
                'success': successes,
                'failed': failures
            }
        
        self.results[name] = result
        
        # Print summary
        if 'error' not in result:
            print(f"\n📊 RESULTS:")
            print(f"  Min:      {result['min_ms']:.2f}ms")
            print(f"  Max:      {result['max_ms']:.2f}ms")
            print(f"  Average:  {result['avg_ms']:.2f}ms")
            print(f"  Median:   {result['median_ms']:.2f}ms")
            print(f"  P95:      {result['p95_ms']:.2f}ms")
            print(f"  Success:  {result['success']}/{iterations}")
            print(f"  Throughput: {result['throughput']:.2f} req/sec")
        
        return result
    
    def test_concurrent(self, name: str, method: str, path: str,
                       payload: dict = None, concurrent_users: int = 5,
                       duration_seconds: int = 10) -> dict:
        """
        Stress test with concurrent users
        
        Returns concurrent performance metrics
        """
        print(f"\n{'='*60}")
        print(f"CONCURRENT TEST: {name}")
        print(f"{'='*60}")
        print(f"Endpoint: {method} {path}")
        print(f"Concurrent Users: {concurrent_users}")
        print(f"Duration: {duration_seconds}s")
        
        times = []
        successes = 0
        failures = 0
        start_total = time.time()
        request_count = 0
        
        def make_request():
            nonlocal successes, failures, request_count
            try:
                start = time.time()
                
                if method.upper() == 'GET':
                    response = requests.get(
                        f"{self.base_url}{path}",
                        timeout=10
                    )
                elif method.upper() == 'POST':
                    response = requests.post(
                        f"{self.base_url}{path}",
                        json=payload,
                        timeout=10,
                        headers={'Content-Type': 'application/json'}
                    )
                
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
                request_count += 1
                
                if response.status_code < 400:
                    successes += 1
                else:
                    failures += 1
                
                return elapsed, response.status_code
            except Exception as e:
                failures += 1
                request_count += 1
                return None, None
        
        # Run concurrent requests
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            end_time = start_total + duration_seconds
            
            while time.time() < end_time:
                for _ in range(concurrent_users):
                    future = executor.submit(make_request)
                    futures.append(future)
                
                # Wait a bit before submitting more
                time.sleep(0.1)
            
            # Wait for all to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except:
                    pass
        
        total_time = time.time() - start_total
        
        result = {
            'name': name,
            'endpoint': f"{method} {path}",
            'concurrent_users': concurrent_users,
            'duration_seconds': duration_seconds,
            'total_requests': request_count,
            'throughput': round(request_count / total_time, 2),  # requests/sec
            'min_ms': round(min(times), 2) if times else 0,
            'max_ms': round(max(times), 2) if times else 0,
            'avg_ms': round(statistics.mean(times), 2) if times else 0,
            'success': successes,
            'failed': failures
        }
        
        self.results[name] = result
        
        print(f"\n📊 RESULTS:")
        print(f"  Total Requests: {request_count}")
        print(f"  Success: {successes}")
        print(f"  Failed: {failures}")
        print(f"  Throughput: {result['throughput']:.2f} req/sec")
        print(f"  Avg Response: {result['avg_ms']:.2f}ms")
        print(f"  Min/Max: {result['min_ms']:.2f}ms / {result['max_ms']:.2f}ms")
        
        return result
    
    def print_summary(self):
        """Print summary of all tests"""
        print(f"\n{'='*60}")
        print("PERFORMANCE TEST SUMMARY")
        print(f"{'='*60}\n")
        
        for name, result in self.results.items():
            print(f"✓ {name}")
            print(f"  Endpoint: {result.get('endpoint', 'N/A')}")
            
            if 'error' in result:
                print(f"  Error: {result['error']}")
            else:
                if 'iterations' in result:
                    # Single-threaded test
                    print(f"  Avg: {result['avg_ms']:.2f}ms | P95: {result['p95_ms']:.2f}ms | Throughput: {result['throughput']:.2f} req/sec")
                else:
                    # Concurrent test
                    print(f"  Throughput: {result['throughput']:.2f} req/sec | Avg: {result['avg_ms']:.2f}ms")
            print()


def run_benchmark_suite():
    """Run complete benchmark suite"""
    print("\n" + "="*60)
    print("GLOBEMARKETMIND PERFORMANCE BENCHMARK")
    print("="*60)
    
    tester = PerformanceTester()
    
    # Test 1: Get all markets
    tester.test_endpoint(
        'Get All Markets',
        'GET',
        '/api/data/markets',
        iterations=20
    )
    
    # Test 2: Get market timeseries
    tester.test_endpoint(
        'Get Market Timeseries (30 days)',
        'GET',
        '/api/history/markets/US_SPX/timeseries?days=30',
        iterations=15
    )
    
    # Test 3: Get rankings
    tester.test_endpoint(
        'Get Market Rankings',
        'GET',
        '/api/history/rankings?metric=mood_index&limit=10',
        iterations=15
    )
    
    # Test 4: Trigger analysis (heavier operation)
    tester.test_endpoint(
        'Trigger Analysis Pipeline',
        'POST',
        '/api/process/analyze',
        iterations=3
    )
    
    # Test 5: Compare markets
    tester.test_endpoint(
        'Compare Multiple Markets',
        'POST',
        '/api/history/compare',
        payload={
            'market_ids': ['US_SPX', 'EU_STOXX', 'JP_NIKKEI'],
            'days': 30,
            'metric': 'mood_index'
        },
        iterations=10
    )
    
    # Test 6: Concurrent test - light endpoint
    tester.test_concurrent(
        'Concurrent Get Markets (5 users, 10s)',
        'GET',
        '/api/data/markets',
        concurrent_users=5,
        duration_seconds=10
    )
    
    # Print final summary
    tester.print_summary()
    
    print("\n✓ Benchmark suite completed")
    print("="*60)


if __name__ == '__main__':
    run_benchmark_suite()
