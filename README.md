# MarketMind - Global Market Sentiment Neural Globe

A Service-Oriented Application (SOA) that visualizes the "emotional state" and interconnections of global financial markets using 3D interactive visualization.

## Project Structure

```
.
├── backend/              # Flask Backend API
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   └── __init__.py
│   ├── tests/
│   ├── requirements.txt
│   └── run.py
├── frontend/            # Web UI (Three.js)
├── docker/              # Docker configuration
│   ├── Dockerfile.backend
│   ├── nginx.conf
│   └── init.sql
├── docker-compose.yml   # Docker Compose configuration
└── README.md
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Run with Docker

```bash
docker-compose up
```

The system will be available at:
- Backend API: http://localhost:5000
- Health check: http://localhost/health

### Local Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

3. Set up database:
```bash
export DATABASE_URL="postgresql://marketmind_user:marketmind_pass@localhost:5432/marketmind"
python -m flask db upgrade
```

4. Run backend:
```bash
cd backend
python run.py
```

## API Endpoints

### Data Service
- `GET /data/markets` - Get all markets
- `GET /data/markets/<market_id>` - Get specific market
- `GET /data/daily_state` - Get all daily states
- `GET /data/daily_state/<market_id>` - Get latest daily state

### Process Service
- `GET /process/snapshot/today` - Get today's market snapshot

## Implementation Phases

- [ ] Phase 1: Foundation Setup (Week 1-2)
- [ ] Phase 2: Core Logic (Week 3-4)
- [ ] Phase 3: Frontend (Week 5)
- [ ] Phase 4: Integration & Testing (Week 6)

## Database

PostgreSQL with pre-populated markets:
- 15 major global markets (DM and EM)
- Tables: market_registry, daily_state, correlation_edges

## Next Steps

1. Implement data fetcher service (yfinance adapter)
2. Implement analytics engine (mood index calculation)
3. Build frontend visualization (Three.js globe)
