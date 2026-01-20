"""
Scheduler service for automated pipeline execution
Manages periodic market analysis runs and data cleanup
"""

import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import func
from app.models.market import MarketRegistry, DailyState, CorrelationEdge
from app.services.adapter import YahooFinanceAdapter
from app.services.analytics import AnalyticsEngine
from app.services.data_service import DataService

logger = logging.getLogger(__name__)

scheduler = None


def run_market_analysis(db):
    """Execute complete market analysis pipeline"""
    try:
        logger.info("=== SCHEDULED MARKET ANALYSIS STARTED ===")
        
        # Stage 1: Fetch market data
        markets = MarketRegistry.query.all()
        market_ids = [m.id for m in markets]
        
        logger.info(f"Fetching data for {len(market_ids)} markets")
        adapter_results = YahooFinanceAdapter.fetch_multiple_markets(
            market_ids=market_ids,
            days_back=30
        )
        
        if not adapter_results['data']:
            logger.warning("No market data fetched")
            return
        
        # Stage 2: Run analytics
        logger.info("Running analytics calculations")
        analytics_results = AnalyticsEngine.process_market_batch(
            markets_data=adapter_results['data']
        )
        
        # Stage 3: Persist to database
        logger.info("Persisting results to database")
        persistence_results = DataService.save_batch_analytics(db, analytics_results)
        
        logger.info(
            f"✓ Market Analysis Complete: "
            f"{persistence_results['markets_saved']} markets saved, "
            f"{persistence_results['correlations_saved']} correlations saved"
        )
        
    except Exception as e:
        logger.error(f"✗ Scheduled market analysis failed: {str(e)}", exc_info=True)


def cleanup_old_data(db, days_to_keep: int = 90):
    """
    Delete market data older than specified number of days
    Keeps correlations independent of date retention
    """
    try:
        cutoff_date = datetime.utcnow().date() - timedelta(days=days_to_keep)
        
        logger.info(f"=== DATA CLEANUP STARTED (keeping {days_to_keep} days) ===")
        
        # Delete old daily states
        deleted_count = db.session.query(DailyState).filter(
            DailyState.date < cutoff_date
        ).delete()
        
        db.session.commit()
        
        logger.info(f"✓ Deleted {deleted_count} old daily state records (before {cutoff_date})")
        
    except Exception as e:
        logger.error(f"✗ Data cleanup failed: {str(e)}", exc_info=True)
        db.session.rollback()


def init_scheduler(app):
    """Initialize APScheduler with Flask app context"""
    global scheduler
    
    if scheduler and scheduler.running:
        logger.warning("Scheduler already running")
        return
    
    scheduler = BackgroundScheduler(daemon=True)
    
    # Job 1: Daily analysis at 9:00 UTC (configurable)
    def daily_analysis():
        with app.app_context():
            run_market_analysis(app.config['db'])
    
    # Job 2: Data cleanup every Sunday at 2:00 UTC
    def weekly_cleanup():
        with app.app_context():
            cleanup_old_data(app.config['db'], days_to_keep=90)
    
    # Add jobs to scheduler
    try:
        # Daily analysis at 9:00 UTC
        scheduler.add_job(
            daily_analysis,
            CronTrigger(hour=9, minute=0, second=0),
            id='daily_market_analysis',
            name='Daily Market Analysis',
            replace_existing=True,
            misfire_grace_time=900
        )
        logger.info("✓ Scheduled: Daily Market Analysis at 09:00 UTC")
        
        # Weekly cleanup every Sunday at 2:00 UTC
        scheduler.add_job(
            weekly_cleanup,
            CronTrigger(day_of_week=6, hour=2, minute=0, second=0),
            id='weekly_data_cleanup',
            name='Weekly Data Cleanup',
            replace_existing=True,
            misfire_grace_time=3600
        )
        logger.info("✓ Scheduled: Weekly Data Cleanup at Sunday 02:00 UTC")
        
        scheduler.start()
        logger.info("✓ APScheduler started successfully")
        
    except Exception as e:
        logger.error(f"✗ Failed to initialize scheduler: {str(e)}", exc_info=True)
        scheduler.shutdown(wait=False)
        scheduler = None


def shutdown_scheduler():
    """Gracefully shutdown scheduler"""
    global scheduler
    
    if scheduler and scheduler.running:
        try:
            scheduler.shutdown(wait=True)
            logger.info("✓ Scheduler shut down gracefully")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {str(e)}")


def get_scheduler_status():
    """Get current scheduler status and jobs"""
    if not scheduler:
        return {
            'status': 'not_initialized',
            'jobs': []
        }
    
    return {
        'status': 'running' if scheduler.running else 'stopped',
        'jobs': [
            {
                'id': job.id,
                'name': job.name,
                'trigger': str(job.trigger),
                'next_run': str(job.next_run_time) if job.next_run_time else 'N/A'
            }
            for job in scheduler.get_jobs()
        ]
    }
