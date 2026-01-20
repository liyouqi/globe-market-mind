"""
Analytics Engine - Calculate market sentiment indicators
Implements the Unified Factor Model from SRS
"""

import numpy as np
import logging
from datetime import datetime
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class FeatureCalculator:
    """Phase 1: Calculate and normalize features using Z-score"""
    
    @staticmethod
    def calculate_return_today(current_price: float, previous_price: float) -> float:
        """Calculate daily return percentage"""
        if previous_price == 0:
            return 0.0
        return ((current_price - previous_price) / previous_price) * 100
    
    @staticmethod
    def calculate_volatility_30d(prices_30d: List[float]) -> float:
        """Calculate 30-day volatility (standard deviation of returns)"""
        if len(prices_30d) < 2:
            return 0.0
        
        prices_array = np.array(prices_30d)
        # Calculate daily returns
        returns = np.diff(prices_array) / prices_array[:-1] * 100
        # Return standard deviation
        return float(np.std(returns))
    
    @staticmethod
    def calculate_volume_score(current_volume: int, prices_30d: List[float], 
                               volumes_30d: List[int] = None) -> float:
        """
        Calculate volume score (current volume relative to 30-day moving average)
        If volumes_30d not provided, use normalized prices as proxy
        """
        if current_volume == 0:
            return 0.0
        
        if volumes_30d and len(volumes_30d) > 0:
            avg_volume = np.mean(volumes_30d)
            if avg_volume == 0:
                return 0.0
            return (current_volume - avg_volume) / avg_volume * 100
        
        # Fallback: use price as proxy (higher price often correlates with higher volume)
        avg_price = np.mean(prices_30d) if prices_30d else 0
        if avg_price == 0:
            return 0.0
        current_price = prices_30d[-1] if prices_30d else 0
        return ((current_price - avg_price) / avg_price) * 100
    
    @staticmethod
    def z_score_normalize(value: float, population_mean: float, 
                         population_std: float) -> float:
        """
        Normalize value using Z-score formula
        Z = (X - μ) / σ
        """
        if population_std == 0:
            return 0.0
        return (value - population_mean) / population_std
    
    @classmethod
    def extract_features(cls, market_data: Dict) -> Dict:
        """
        Extract and calculate features from raw market data
        
        Returns:
            {
                'return_today': float,
                'volatility_30d': float,
                'volume_score': float,
                'return_normalized': float,  # Z-score
                'volatility_normalized': float,
                'volume_normalized': float
            }
        """
        prices_30d = market_data.get('prices_30d', [])
        current_price = market_data.get('close_price', 0)
        current_volume = market_data.get('volume', 0)
        
        # Calculate raw features
        if len(prices_30d) > 1:
            prev_price = prices_30d[-2]
            return_today = cls.calculate_return_today(current_price, prev_price)
        else:
            return_today = 0.0
        
        volatility_30d = cls.calculate_volatility_30d(prices_30d)
        volume_score = cls.calculate_volume_score(current_volume, prices_30d)
        
        # Normalize using population statistics (across all markets would be ideal)
        # For now, use simple normalization with assumed population params
        return_normalized = cls.z_score_normalize(return_today, 0, 2.0)  # Assume std ~2%
        volatility_normalized = cls.z_score_normalize(volatility_30d, 2.0, 1.0)  # Assume std ~1
        volume_normalized = cls.z_score_normalize(volume_score, 0, 50)  # Assume std ~50%
        
        return {
            'return_today': return_today,
            'volatility_30d': volatility_30d,
            'volume_score': volume_score,
            'return_normalized': return_normalized,
            'volatility_normalized': volatility_normalized,
            'volume_normalized': volume_normalized,
        }


class MoodEngine:
    """Phase 2: Calculate mood index using Unified Factor Model"""
    
    # Default weights from SRS
    DEFAULT_WEIGHTS = {
        'return': 0.5,
        'volatility': -0.3,  # Negative: high volatility = bearish
        'volume': 0.2,
    }
    
    @classmethod
    def calculate_mood_index(cls, features: Dict, weights: Dict = None) -> float:
        """
        Calculate mood index using Unified Factor Model
        
        Formula:
        Mood Index = w1 * return + w2 * volatility + w3 * volume
        
        Args:
            features: Normalized feature dict from FeatureCalculator
            weights: Custom weights (default: DEFAULT_WEIGHTS)
            
        Returns:
            Mood index in range [-1.0, 1.0]
        """
        if weights is None:
            weights = cls.DEFAULT_WEIGHTS
        
        mood = (
            weights['return'] * features.get('return_normalized', 0) +
            weights['volatility'] * features.get('volatility_normalized', 0) +
            weights['volume'] * features.get('volume_normalized', 0)
        )
        
        # Clamp to [-1.0, 1.0]
        mood = max(-1.0, min(1.0, mood))
        
        return round(mood, 4)
    
    @staticmethod
    def mood_to_level(mood_index: float) -> str:
        """
        Convert mood index to human-readable level
        
        -1.0 to -0.5: very_bearish
        -0.5 to -0.1: bearish
        -0.1 to 0.1: neutral
        0.1 to 0.5: bullish
        0.5 to 1.0: very_bullish
        """
        if mood_index < -0.5:
            return 'very_bearish'
        elif mood_index < -0.1:
            return 'bearish'
        elif mood_index < 0.1:
            return 'neutral'
        elif mood_index < 0.5:
            return 'bullish'
        else:
            return 'very_bullish'
    
    @classmethod
    def calculate_mood(cls, market_data: Dict, weights: Dict = None) -> Dict:
        """
        Complete mood calculation from raw market data
        
        Returns:
            {
                'mood_index': float,
                'mood_level': str,
                'features': {...}
            }
        """
        # Calculate features
        features = FeatureCalculator.extract_features(market_data)
        
        # Calculate mood index
        mood_index = cls.calculate_mood_index(features, weights)
        
        # Get mood level
        mood_level = cls.mood_to_level(mood_index)
        
        return {
            'mood_index': mood_index,
            'mood_level': mood_level,
            'features': features,
        }


class CorrelationCalculator:
    """Phase 3: Calculate correlation between markets"""
    
    CORRELATION_THRESHOLD = 0.6  # Only show edges with correlation > 0.6
    
    @staticmethod
    def calculate_pearson_correlation(returns_a: List[float], 
                                     returns_b: List[float]) -> float:
        """
        Calculate Pearson correlation coefficient between two return series
        
        Returns:
            Correlation in range [-1.0, 1.0]
        """
        if len(returns_a) < 2 or len(returns_b) < 2:
            return 0.0
        
        arr_a = np.array(returns_a)
        arr_b = np.array(returns_b)
        
        # Ensure same length
        min_len = min(len(arr_a), len(arr_b))
        arr_a = arr_a[-min_len:]
        arr_b = arr_b[-min_len:]
        
        correlation = np.corrcoef(arr_a, arr_b)[0, 1]
        
        # Handle NaN
        if np.isnan(correlation):
            return 0.0
        
        return round(float(correlation), 4)
    
    @classmethod
    def extract_returns(cls, prices_30d: List[float]) -> List[float]:
        """Extract daily returns from price series"""
        if len(prices_30d) < 2:
            return []
        
        prices_array = np.array(prices_30d)
        returns = np.diff(prices_array) / prices_array[:-1] * 100
        return returns.tolist()
    
    @classmethod
    def calculate_correlations(cls, markets_data: Dict[str, Dict]) -> Dict:
        """
        Calculate correlations between all market pairs
        
        Args:
            markets_data: {
                'US_SPX': {'prices_30d': [...]},
                'EU_STOXX': {'prices_30d': [...]},
                ...
            }
            
        Returns:
            {
                'edges': [
                    {
                        'source': 'US_SPX',
                        'target': 'EU_STOXX',
                        'weight': 0.75
                    },
                    ...
                ]
            }
        """
        edges = []
        market_ids = list(markets_data.keys())
        
        # Calculate returns for all markets
        returns_map = {}
        for market_id, data in markets_data.items():
            returns = cls.extract_returns(data.get('prices_30d', []))
            returns_map[market_id] = returns
        
        # Calculate pairwise correlations
        for i in range(len(market_ids)):
            for j in range(i + 1, len(market_ids)):
                market_a = market_ids[i]
                market_b = market_ids[j]
                
                returns_a = returns_map.get(market_a, [])
                returns_b = returns_map.get(market_b, [])
                
                if not returns_a or not returns_b:
                    continue
                
                correlation = cls.calculate_pearson_correlation(returns_a, returns_b)
                
                # Only include significant correlations
                if abs(correlation) >= cls.CORRELATION_THRESHOLD:
                    edges.append({
                        'source': market_a,
                        'target': market_b,
                        'weight': correlation,
                        'type': 'positive' if correlation > 0 else 'negative'
                    })
        
        # Sort by absolute correlation strength (descending)
        edges.sort(key=lambda x: abs(x['weight']), reverse=True)
        
        return {'edges': edges}


class AnalyticsEngine:
    """
    Main Analytics Engine - orchestrates all calculations
    Combines Feature Calculator, Mood Engine, and Correlation Calculator
    """
    
    @classmethod
    def calculate_market_analytics(cls, market_data: Dict) -> Dict:
        """
        Calculate complete analytics for a single market
        
        Returns all computed fields ready to save to database:
        {
            'mood_index': float,
            'mood_level': str,
            'volatility_30d': float,
            'trend_strength': float,
            ...
        }
        """
        mood_result = MoodEngine.calculate_mood(market_data)
        features = mood_result['features']
        
        # Calculate trend strength (how strong is the return signal)
        trend_strength = abs(features.get('return_normalized', 0))
        
        return {
            'mood_index': mood_result['mood_index'],
            'mood_level': mood_result['mood_level'],
            'volatility_30d': round(features.get('volatility_30d', 0), 4),
            'trend_strength': round(trend_strength, 4),
        }
    
    @classmethod
    def process_market_batch(cls, markets_data: Dict[str, Dict]) -> Dict:
        """
        Process analytics for multiple markets in one batch
        
        Returns:
            {
                'date': '2026-01-18',
                'markets': {
                    'US_SPX': {
                        'mood_index': 0.45,
                        'mood_level': 'bullish',
                        ...
                    },
                    ...
                },
                'correlations': {
                    'edges': [...]
                }
            }
        """
        results = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'markets': {},
            'correlations': {}
        }
        
        # Calculate analytics for each market
        for market_id, market_data in markets_data.items():
            try:
                analytics = cls.calculate_market_analytics(market_data)
                results['markets'][market_id] = analytics
            except Exception as e:
                logger.error(f"Error calculating analytics for {market_id}: {str(e)}")
                results['markets'][market_id] = None
        
        # Calculate correlations
        try:
            results['correlations'] = CorrelationCalculator.calculate_correlations(markets_data)
        except Exception as e:
            logger.error(f"Error calculating correlations: {str(e)}")
            results['correlations'] = {'edges': []}
        
        return results
