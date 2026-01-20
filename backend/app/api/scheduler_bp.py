"""
Scheduler management API endpoints
Monitor and control scheduled tasks
"""

from flask import Blueprint, jsonify, current_app
import logging
from app.services.scheduler import (
    get_scheduler_status,
    run_market_analysis,
    cleanup_old_data
)

logger = logging.getLogger(__name__)

scheduler_bp = Blueprint('scheduler', __name__, url_prefix='/api/scheduler')


@scheduler_bp.route('/status', methods=['GET'])
def get_status():
    """Get scheduler status
    ---
    tags:
      - Scheduler
    responses:
      200:
        description: Scheduler status
    """
    status = get_scheduler_status()
    return jsonify({'scheduler': status}), 200


@scheduler_bp.route('/trigger-analysis', methods=['POST'])
def trigger_manual_analysis():
    """Trigger market analysis
    ---
    tags:
      - Scheduler
    responses:
      200:
        description: Analysis triggered
    """
    db = current_app.config['db']
    
    try:
        # Run in background
        run_market_analysis(db)
        
        return jsonify({
            'status': 'triggered',
            'message': 'Market analysis triggered successfully'
        }), 202
        
    except Exception as e:
        logger.error(f"Error triggering manual analysis: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@scheduler_bp.route('/trigger-cleanup', methods=['POST'])
def trigger_manual_cleanup():
    """Trigger data cleanup
    ---
    tags:
      - Scheduler
    responses:
      202:
        description: Cleanup triggered
    """
    db = current_app.config['db']
    days_to_keep = int(current_app.config.get('DAYS_TO_KEEP', 90))
    
    try:
        cleanup_old_data(db, days_to_keep=days_to_keep)
        
        return jsonify({
            'status': 'triggered',
            'message': f'Data cleanup triggered successfully (keeping {days_to_keep} days)'
        }), 202
        
    except Exception as e:
        logger.error(f"Error triggering manual cleanup: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
