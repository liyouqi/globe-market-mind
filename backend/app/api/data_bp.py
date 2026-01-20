from flask import Blueprint, jsonify
from app import db
from app.models.market import MarketRegistry, DailyState

data_bp = Blueprint('data', __name__, url_prefix='/api/data')

@data_bp.route('/markets', methods=['GET'])
def get_markets():
    """Get all global markets
    ---
    tags:
      - Markets
    responses:
      200:
        description: List of all markets
    """
    markets = MarketRegistry.query.all()
    return jsonify([market.to_dict() for market in markets]), 200

@data_bp.route('/markets/<market_id>', methods=['GET'])
def get_market(market_id):
    """Get single market details
    ---
    tags:
      - Markets
    responses:
      200:
        description: Market details
      404:
        description: Market not found
    """
    market = MarketRegistry.query.get(market_id)
    if not market:
        return jsonify({'error': 'Market not found'}), 404
    return jsonify(market.to_dict()), 200

@data_bp.route('/daily_state', methods=['GET'])
def get_daily_states():
    """Get daily states for all markets
    ---
    tags:
      - Markets
    responses:
      200:
        description: Daily states data
    """
    states = DailyState.query.all()
    return jsonify([state.to_dict() for state in states]), 200

@data_bp.route('/daily_state/<market_id>', methods=['GET'])
def get_daily_state(market_id):
    """Get latest daily state for a market
    ---
    tags:
      - Markets
    responses:
      200:
        description: Daily state data
      404:
        description: No data found
    """
    state = DailyState.query.filter_by(market_id=market_id).order_by(DailyState.date.desc()).first()
    if not state:
        return jsonify({'error': 'No data found'}), 404
    return jsonify(state.to_dict()), 200
