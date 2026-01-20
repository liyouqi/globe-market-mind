"""
Data Service - Persist analytics results to database
"""

import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.models.market import DailyState, CorrelationEdge, MarketRegistry

logger = logging.getLogger(__name__)


class DataService:
    """Service to persist market analytics to database"""
    
    @staticmethod
    def save_daily_state(db, market_id: str, analytics: dict) -> bool:
        """
        Save daily state record for a market
        
        Args:
            db: SQLAlchemy database instance
            market_id: Market identifier (e.g., 'US_SPX')
            analytics: Dict from AnalyticsEngine.calculate_market_analytics()
                {
                    'mood_index': 0.45,
                    'mood_level': 'bullish',
                    'volatility_30d': 0.55,
                    'trend_strength': 0.15,
                    ...
                }
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if market exists
            market = MarketRegistry.query.filter_by(id=market_id).first()
            if not market:
                logger.warning(f"Market {market_id} not found in registry")
                return False
            
            # Create or update daily state
            today = datetime.utcnow().date()
            daily_state = DailyState.query.filter_by(
                market_id=market_id,
                date=today
            ).first()
            
            if daily_state:
                # Update existing record
                daily_state.mood_index = analytics.get('mood_index', 0)
                daily_state.mood_level = analytics.get('mood_level', 'neutral')
                daily_state.volatility_30d = analytics.get('volatility_30d', 0)
                daily_state.trend_strength = analytics.get('trend_strength', 0)
                daily_state.updated_at = datetime.utcnow()
            else:
                # Create new record - need market data from analytics
                daily_state = DailyState(
                    market_id=market_id,
                    date=today,
                    close_price=analytics.get('close_price', 0),
                    volume=analytics.get('volume', 0),
                    change_pct=analytics.get('change_pct', 0),
                    mood_index=analytics.get('mood_index', 0),
                    mood_level=analytics.get('mood_level', 'neutral'),
                    volatility_30d=analytics.get('volatility_30d', 0),
                    trend_strength=analytics.get('trend_strength', 0),
                )
                db.session.add(daily_state)
            
            db.session.commit()
            logger.info(f"Saved daily state for {market_id}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database error saving daily state for {market_id}: {str(e)}")
            db.session.rollback()
            return False
        except Exception as e:
            logger.error(f"Error saving daily state for {market_id}: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def save_correlation_edge(db, source: str, target: str, 
                             correlation_value: float) -> bool:
        """
        Save correlation edge between two markets
        
        Args:
            db: SQLAlchemy database instance
            source: Source market ID
            target: Target market ID
            correlation_value: Pearson correlation coefficient
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure consistent ordering
            if source > target:
                source, target = target, source
            
            # Check if edge already exists
            existing_edge = CorrelationEdge.query.filter_by(
                source_market_id=source,
                target_market_id=target
            ).first()
            
            if existing_edge:
                # Update correlation value
                existing_edge.correlation_value = correlation_value
                existing_edge.updated_at = datetime.utcnow()
            else:
                # Create new edge
                edge = CorrelationEdge(
                    source_market_id=source,
                    target_market_id=target,
                    correlation_value=correlation_value
                )
                db.session.add(edge)
            
            db.session.commit()
            logger.info(f"Saved correlation edge {source} ↔ {target}: {correlation_value:.4f}")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"Database error saving correlation: {str(e)}")
            db.session.rollback()
            return False
        except Exception as e:
            logger.error(f"Error saving correlation: {str(e)}")
            db.session.rollback()
            return False
    
    @classmethod
    def save_batch_analytics(cls, db, analytics_results: dict) -> dict:
        """
        Save complete analytics batch to database
        
        Args:
            db: SQLAlchemy database instance
            analytics_results: Dict from AnalyticsEngine.process_market_batch()
                {
                    'date': '2026-01-18',
                    'markets': {
                        'US_SPX': {'mood_index': 0.45, ...},
                        'EU_STOXX': {'mood_index': -0.15, ...},
                        ...
                    },
                    'correlations': {
                        'edges': [
                            {'source': 'US_SPX', 'target': 'EU_STOXX', 'weight': 0.75, ...},
                            ...
                        ]
                    }
                }
        
        Returns:
            {
                'status': 'success' | 'partial' | 'failed',
                'markets_saved': int,
                'markets_failed': int,
                'correlations_saved': int,
                'correlations_failed': int,
                'details': {
                    'saved_markets': ['US_SPX', ...],
                    'failed_markets': ['EU_STOXX', ...],
                    ...
                }
            }
        """
        results = {
            'status': 'success',
            'markets_saved': 0,
            'markets_failed': 0,
            'correlations_saved': 0,
            'correlations_failed': 0,
            'details': {
                'saved_markets': [],
                'failed_markets': [],
                'saved_correlations': [],
                'failed_correlations': []
            }
        }
        
        # Save market analytics
        if analytics_results.get('markets'):
            for market_id, analytics in analytics_results['markets'].items():
                if analytics:  # Skip None values
                    if cls.save_daily_state(db, market_id, analytics):
                        results['markets_saved'] += 1
                        results['details']['saved_markets'].append(market_id)
                    else:
                        results['markets_failed'] += 1
                        results['details']['failed_markets'].append(market_id)
        
        # Save correlations
        if analytics_results.get('correlations') and analytics_results['correlations'].get('edges'):
            for edge in analytics_results['correlations']['edges']:
                if cls.save_correlation_edge(
                    db,
                    edge['source'],
                    edge['target'],
                    edge['weight']
                ):
                    results['correlations_saved'] += 1
                    results['details']['saved_correlations'].append(
                        f"{edge['source']} ↔ {edge['target']}: {edge['weight']:.4f}"
                    )
                else:
                    results['correlations_failed'] += 1
                    results['details']['failed_correlations'].append(
                        f"{edge['source']} ↔ {edge['target']}"
                    )
        
        # Determine overall status
        if results['markets_failed'] > 0 or results['correlations_failed'] > 0:
            results['status'] = 'partial'
        if results['markets_saved'] == 0 and results['correlations_saved'] == 0:
            results['status'] = 'failed'
        
        logger.info(
            f"Batch save complete: {results['markets_saved']} markets, "
            f"{results['correlations_saved']} correlations"
        )
        
        return results
    
    @staticmethod
    def get_latest_snapshot() -> dict:
        """
        Retrieve latest analytics snapshot for all markets
        
        Returns:
            {
                'date': '2026-01-18',
                'markets': {
                    'US_SPX': {
                        'market_id': 'US_SPX',
                        'date': '2026-01-18',
                        'mood_index': 0.45,
                        'mood_level': 'bullish',
                        'volatility_30d': 0.55,
                        'trend_strength': 0.15,
                        ...
                    },
                    ...
                },
                'correlations': [
                    {
                        'source': 'US_SPX',
                        'target': 'EU_STOXX',
                        'correlation_value': 0.75
                    },
                    ...
                ]
            }
        """
        try:
            # Get latest daily states (grouped by date, take most recent)
            daily_states = DailyState.query.order_by(
                DailyState.date.desc(),
                DailyState.market_id
            ).all()
            
            if not daily_states:
                return {
                    'date': None,
                    'markets': {},
                    'correlations': []
                }
            
            latest_date = daily_states[0].date
            
            # Filter for latest date only
            latest_states = [ds for ds in daily_states if ds.date == latest_date]
            
            markets_dict = {}
            for state in latest_states:
                markets_dict[state.market_id] = state.to_dict()
            
            # Get correlations
            correlations = CorrelationEdge.query.all()
            correlations_list = [
                {
                    'source': c.source_market_id,
                    'target': c.target_market_id,
                    'correlation_value': c.correlation_value
                }
                for c in correlations
            ]
            
            return {
                'date': latest_date.isoformat() if latest_date else None,
                'markets': markets_dict,
                'correlations': correlations_list
            }
            
        except Exception as e:
            logger.error(f"Error retrieving latest snapshot: {str(e)}")
            return {
                'date': None,
                'markets': {},
                'correlations': []
            }
