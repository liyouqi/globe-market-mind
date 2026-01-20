"""
History and analytics query API endpoints
Provides historical data retrieval, trend analysis, and market comparisons
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, timedelta
import logging
from sqlalchemy import func, desc
from app.models.market import MarketRegistry, DailyState, CorrelationEdge

logger = logging.getLogger(__name__)

history_bp = Blueprint('history', __name__, url_prefix='/api/history')


@history_bp.route('/markets/<market_id>/timeseries', methods=['GET'])
def get_market_timeseries(market_id: str):
    """
    Get time series data for a single market
    
    Query parameters:
        - days: Number of days to look back (default: 30)
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
    
    Returns:
        {
            'market_id': 'US_SPX',
            'data': [
                {
                    'date': '2026-01-20',
                    'mood_index': 0.45,
                    'mood_level': 'bullish',
                    'volatility_30d': 0.55,
                    'trend_strength': 0.15,
                    'close_price': 4535.62,
                    'volume': 450000000
                },
                ...
            ]
        }
    """
    db = current_app.config['db']
    
    try:
        # Verify market exists
        market = MarketRegistry.query.filter_by(id=market_id).first()
        if not market:
            return jsonify({'error': 'Market not found'}), 404
        
        # Parse query parameters
        days = request.args.get('days', 30, type=int)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # Build date range
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end_date = datetime.utcnow().date()
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = end_date - timedelta(days=days)
        
        # Query historical data
        states = DailyState.query.filter(
            DailyState.market_id == market_id,
            DailyState.date >= start_date,
            DailyState.date <= end_date
        ).order_by(DailyState.date.asc()).all()
        
        if not states:
            return jsonify({
                'market_id': market_id,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'data': []
            }), 200
        
        data = [state.to_dict() for state in states]
        
        return jsonify({
            'market_id': market_id,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
                'days': len(data)
            },
            'data': data
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving timeseries for {market_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@history_bp.route('/compare', methods=['POST'])
def compare_markets():
    """
    Compare mood index trends between multiple markets
    
    Request body:
        {
            'market_ids': ['US_SPX', 'EU_STOXX', 'JP_NIKKEI'],
            'days': 30,
            'metric': 'mood_index'  # or 'volatility_30d', 'trend_strength'
        }
    
    Returns:
        {
            'comparison': {
                'metric': 'mood_index',
                'date_range': {'start': '2025-12-21', 'end': '2026-01-20'},
                'markets': {
                    'US_SPX': {
                        'current': 0.45,
                        'previous': 0.38,
                        'change': 0.07,
                        'trend': 'up',
                        'history': [0.30, 0.35, 0.38, 0.45, ...]
                    },
                    ...
                }
            }
        }
    """
    db = current_app.config['db']
    
    try:
        payload = request.get_json()
        market_ids = payload.get('market_ids', [])
        days = payload.get('days', 30)
        metric = payload.get('metric', 'mood_index')
        
        if not market_ids:
            return jsonify({'error': 'market_ids required'}), 400
        
        if metric not in ['mood_index', 'volatility_30d', 'trend_strength']:
            return jsonify({'error': 'Invalid metric'}), 400
        
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        comparison = {
            'comparison': {
                'metric': metric,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'markets': {}
            }
        }
        
        for market_id in market_ids:
            states = DailyState.query.filter(
                DailyState.market_id == market_id,
                DailyState.date >= start_date,
                DailyState.date <= end_date
            ).order_by(DailyState.date.asc()).all()
            
            if not states:
                comparison['comparison']['markets'][market_id] = {
                    'error': 'No data available'
                }
                continue
            
            values = [getattr(state, metric, 0) for state in states]
            
            comparison['comparison']['markets'][market_id] = {
                'current': values[-1],
                'previous': values[-2] if len(values) > 1 else values[-1],
                'change': values[-1] - (values[-2] if len(values) > 1 else values[-1]),
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'trend': 'up' if values[-1] > values[0] else 'down',
                'history': values
            }
        
        return jsonify(comparison), 200
        
    except Exception as e:
        logger.error(f"Error comparing markets: {str(e)}")
        return jsonify({'error': str(e)}), 500


@history_bp.route('/rankings', methods=['GET'])
def get_market_rankings():
    """
    Get ranked markets by sentiment metric
    
    Query parameters:
        - metric: 'mood_index', 'volatility_30d', 'trend_strength' (default: mood_index)
        - order: 'asc' or 'desc' (default: desc for mood, asc for volatility)
        - limit: Top N markets (default: 15)
    
    Returns:
        {
            'rankings': {
                'metric': 'mood_index',
                'timestamp': '2026-01-20T10:30:00',
                'top': [
                    {'rank': 1, 'market_id': 'IN_SENSEX', 'value': 0.4241, 'change': 0.05},
                    ...
                ],
                'bottom': [...]
            }
        }
    """
    db = current_app.config['db']
    
    try:
        metric = request.args.get('metric', 'mood_index')
        order = request.args.get('order', 'desc')
        limit = request.args.get('limit', 15, type=int)
        
        if metric not in ['mood_index', 'volatility_30d', 'trend_strength']:
            return jsonify({'error': 'Invalid metric'}), 400
        
        # Get latest date
        latest_date_result = db.session.query(
            func.max(DailyState.date)
        ).scalar()
        
        if not latest_date_result:
            return jsonify({'error': 'No data available'}), 404
        
        latest_date = latest_date_result
        previous_date = latest_date - timedelta(days=1)
        
        # Get today's rankings
        query = DailyState.query.filter_by(date=latest_date)
        
        if order.lower() == 'desc':
            query = query.order_by(desc(getattr(DailyState, metric)))
        else:
            query = query.order_by(getattr(DailyState, metric))
        
        today_states = query.limit(limit).all()
        
        # Get previous day's values for change calculation
        yesterday_states = {
            state.market_id: state
            for state in DailyState.query.filter_by(date=previous_date).all()
        }
        
        top_rankings = []
        for rank, state in enumerate(today_states, 1):
            value = getattr(state, metric, 0)
            yesterday_value = getattr(
                yesterday_states.get(state.market_id),
                metric,
                value
            )
            change = value - yesterday_value if yesterday_states.get(state.market_id) else 0
            
            top_rankings.append({
                'rank': rank,
                'market_id': state.market_id,
                'value': value,
                'change': round(change, 4),
                'trend': 'up' if change > 0 else 'down' if change < 0 else 'stable'
            })
        
        # Get bottom rankings
        if order.lower() == 'desc':
            query = DailyState.query.filter_by(date=latest_date).order_by(
                getattr(DailyState, metric)
            )
        else:
            query = DailyState.query.filter_by(date=latest_date).order_by(
                desc(getattr(DailyState, metric))
            )
        
        bottom_states = query.limit(limit).all()
        
        bottom_rankings = []
        for rank, state in enumerate(bottom_states, 1):
            value = getattr(state, metric, 0)
            yesterday_value = getattr(
                yesterday_states.get(state.market_id),
                metric,
                value
            )
            change = value - yesterday_value if yesterday_states.get(state.market_id) else 0
            
            bottom_rankings.append({
                'rank': rank,
                'market_id': state.market_id,
                'value': value,
                'change': round(change, 4),
                'trend': 'up' if change > 0 else 'down' if change < 0 else 'stable'
            })
        
        return jsonify({
            'rankings': {
                'metric': metric,
                'date': latest_date.isoformat(),
                'top': top_rankings,
                'bottom': bottom_rankings
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting rankings: {str(e)}")
        return jsonify({'error': str(e)}), 500


@history_bp.route('/correlation-network', methods=['GET'])
def get_correlation_network():
    """
    Get complete correlation network of markets
    
    Returns:
        {
            'network': {
                'nodes': [
                    {'id': 'US_SPX', 'mood_index': 0.45, 'volatility': 0.55},
                    ...
                ],
                'edges': [
                    {'source': 'US_SPX', 'target': 'EU_STOXX', 'weight': 0.75},
                    ...
                ]
            }
        }
    """
    db = current_app.config['db']
    
    try:
        # Get latest snapshot for all markets
        latest_date_result = db.session.query(
            func.max(DailyState.date)
        ).scalar()
        
        if not latest_date_result:
            return jsonify({'error': 'No data available'}), 404
        
        latest_date = latest_date_result
        
        # Get all latest states as nodes
        latest_states = DailyState.query.filter_by(date=latest_date).all()
        
        nodes = [
            {
                'id': state.market_id,
                'mood_index': state.mood_index,
                'mood_level': state.mood_level,
                'volatility_30d': state.volatility_30d,
                'trend_strength': state.trend_strength
            }
            for state in latest_states
        ]
        
        # Get all correlations as edges
        correlations = CorrelationEdge.query.all()
        
        edges = [
            {
                'source': corr.source_market_id,
                'target': corr.target_market_id,
                'weight': corr.correlation_value,
                'type': 'positive' if corr.correlation_value > 0 else 'negative'
            }
            for corr in correlations
        ]
        
        return jsonify({
            'network': {
                'date': latest_date.isoformat(),
                'nodes': nodes,
                'edges': edges
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting correlation network: {str(e)}")
        return jsonify({'error': str(e)}), 500
