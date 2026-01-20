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
    """
    Get current scheduler status and job information
    
    Returns:
        {
            'scheduler': {
                'status': 'running' | 'stopped' | 'not_initialized',
                'jobs': [
                    {
                        'id': 'daily_market_analysis',
                        'name': 'Daily Market Analysis',
                        'trigger': 'cron[hour=9]',
                        'next_run': '2026-01-21T09:00:00'
                    },
                    ...
                ]
            }
        }
    """
    status = get_scheduler_status()
    return jsonify({'scheduler': status}), 200


@scheduler_bp.route('/trigger-analysis', methods=['POST'])
def trigger_manual_analysis():
    """
    Manually trigger market analysis (useful for testing)
    Does not wait for completion
    
    Returns:
        {
            'status': 'triggered',
            'message': 'Market analysis triggered manually'
        }
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
    """
    Manually trigger data cleanup (useful for testing)
    
    Query parameters:
        - days_to_keep: Number of days of data to retain (default: 90)
    
    Returns:
        {
            'status': 'triggered',
            'message': 'Data cleanup triggered successfully'
        }
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
