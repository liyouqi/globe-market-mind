"""
Process orchestration blueprint
Implements data processing pipelines
"""

from flask import Blueprint, jsonify, request, current_app
import logging
from app.models.market import MarketRegistry
from app.services.adapter import YahooFinanceAdapter
from app.services.analytics import AnalyticsEngine
from app.services.data_service import DataService

logger = logging.getLogger(__name__)

process_bp = Blueprint('process', __name__, url_prefix='/api/process')


@process_bp.route('/analyze', methods=['POST'])
def trigger_analysis():
    """Analyze all markets
    ---
    tags:
      - Processing
    responses:
      200:
        description: Analysis results
    """
    db = current_app.config['db']
    
    try:
        # Stage 1: Fetch market data
        logger.info("Pipeline Stage 1: Fetching market data")
        
        markets = MarketRegistry.query.all()
        market_ids = [m.id for m in markets]
        
        adapter_results = YahooFinanceAdapter.fetch_multiple_markets(
            market_ids=market_ids,
            days_back=30
        )
        
        fetch_status = {
            'markets_fetched': len(adapter_results['success']),
            'markets_failed': len(adapter_results['failed']),
            'success': adapter_results['success'],
            'failed': adapter_results['failed']
        }
        
        if not adapter_results['data']:
            return jsonify({
                'status': 'failed',
                'error': 'No market data could be fetched',
                'pipeline': {
                    'data_fetch': fetch_status,
                    'analytics': None,
                    'persistence': None
                }
            }), 500
        
        logger.info(f"Stage 1 complete: {fetch_status['markets_fetched']} markets fetched")
        
        # Stage 2: Run analytics
        logger.info("Pipeline Stage 2: Running analytics")
        
        analytics_results = AnalyticsEngine.process_market_batch(
            markets_data=adapter_results['data']
        )
        
        # Merge original adapter data with analytics results
        for market_id in analytics_results['markets']:
            if market_id in adapter_results['data']:
                original_data = adapter_results['data'][market_id]
                analytics_results['markets'][market_id].update({
                    'close_price': original_data.get('close_price', 0),
                    'volume': original_data.get('volume', 0),
                    'change_pct': original_data.get('change_pct', 0),
                })
        
        markets_analyzed = len([v for v in analytics_results['markets'].values() if v])
        correlations_found = len(analytics_results['correlations'].get('edges', []))
        
        analytics_status = {
            'markets_analyzed': markets_analyzed,
            'correlations_found': correlations_found
        }
        
        logger.info(f"Stage 2 complete: {markets_analyzed} markets analyzed, {correlations_found} correlations found")
        
        # Stage 3: Persist to database
        logger.info("Pipeline Stage 3: Persisting to database")
        
        persistence_results = DataService.save_batch_analytics(
            db=db,
            analytics_results=analytics_results
        )
        
        # Determine overall status
        overall_status = 'success'
        if persistence_results['status'] != 'success':
            overall_status = persistence_results['status']
        
        return jsonify({
            'status': overall_status,
            'pipeline': {
                'data_fetch': fetch_status,
                'analytics': analytics_status,
                'persistence': {
                    'status': persistence_results['status'],
                    'markets_saved': persistence_results['markets_saved'],
                    'markets_failed': persistence_results['markets_failed'],
                    'correlations_saved': persistence_results['correlations_saved'],
                    'correlations_failed': persistence_results['correlations_failed'],
                }
            },
            'timestamp': analytics_results.get('date')
        }), 200 if overall_status == 'success' else 207
        
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@process_bp.route('/snapshot', methods=['GET'])
def get_snapshot():
    """Get latest analytics snapshot
    ---
    tags:
      - Processing
    responses:
      200:
        description: Latest snapshot data
    """
    try:
        snapshot = DataService.get_latest_snapshot()
        
        if not snapshot['markets']:
            return jsonify({
                'status': 'no_data',
                'message': 'No analytics data available. Run POST /api/process/analyze first.'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': snapshot
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving snapshot: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
