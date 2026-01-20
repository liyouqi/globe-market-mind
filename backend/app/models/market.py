from app import db
from datetime import datetime

class MarketRegistry(db.Model):
    __tablename__ = 'market_registry'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    market_group = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'market_group': self.market_group,
            'country': self.country
        }

class DailyState(db.Model):
    __tablename__ = 'daily_state'
    
    id = db.Column(db.Integer, primary_key=True)
    market_id = db.Column(db.String(50), db.ForeignKey('market_registry.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.BigInteger)
    change_pct = db.Column(db.Float)
    mood_index = db.Column(db.Float)
    mood_level = db.Column(db.String(20))
    volatility_30d = db.Column(db.Float)
    trend_strength = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    market = db.relationship('MarketRegistry', backref='daily_states')
    
    def to_dict(self):
        return {
            'id': self.id,
            'market_id': self.market_id,
            'date': self.date.isoformat(),
            'close_price': self.close_price,
            'volume': self.volume,
            'change_pct': self.change_pct,
            'mood_index': self.mood_index,
            'mood_level': self.mood_level,
            'volatility_30d': self.volatility_30d,
            'trend_strength': self.trend_strength
        }

class CorrelationEdge(db.Model):
    __tablename__ = 'correlation_edges'
    
    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.String(50), db.ForeignKey('market_registry.id'), nullable=False)
    target_id = db.Column(db.String(50), db.ForeignKey('market_registry.id'), nullable=False)
    correlation_value = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    source = db.relationship('MarketRegistry', foreign_keys=[source_id])
    target = db.relationship('MarketRegistry', foreign_keys=[target_id])
    
    def to_dict(self):
        return {
            'source': self.source_id,
            'target': self.target_id,
            'weight': self.correlation_value,
            'date': self.date.isoformat()
        }
