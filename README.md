# GlobeMarketMind - Global Market Sentiment Analysis

This is a Flask-based system that analyzes the mood/sentiment of **79 global stock markets** across 6 continents. It automatically calculates a "mood index" for each market and shows how different markets are correlated with each other.

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐      │
│  │  Web Browser     │  │  API Client      │  │  3D Visualization │      │
│  │  (Swagger UI)    │  │  (curl/Postman)  │  │  (Three.js)       │      │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘      │
└───────────┼────────────────────┼────────────────────┼──────────────────┘
            │                    │                    │
            └────────────────────┼────────────────────┘
                                 ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                    API GATEWAY (Nginx:80)                                 │
│         Routes /api/* → Backend | /apidocs → Swagger UI                  │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                   BACKEND SERVICE (Flask:5000)                            │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  LAYER 1: Process Orchestration (process_bp.py)                    │ │
│  │  • Pipeline coordination                                            │ │
│  │  • Manual/scheduled triggers                                        │ │
│  │  • Snapshot generation                                              │ │
│  └───────────────────────────┬────────────────────────────────────────┘ │
│                              ↓                                            │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  LAYER 2: Business Logic (analytics.py)                            │ │
│  │  • FeatureCalculator: Volatility, Returns, Volume Ratios          │ │
│  │  • MoodEngine: Mood Index = 0.5×Return - 0.3×Vol + 0.2×Volume    │ │
│  │  • CorrelationCalculator: Pearson correlation between markets     │ │
│  └───────────────────────────┬────────────────────────────────────────┘ │
│                              ↓                                            │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  LAYER 3: Data Adapter (adapter.py)                                │ │
│  │  • Yahoo Finance API integration                                   │ │
│  │  • 79 market symbols mapping (US_SPX → ^GSPC)                     │ │
│  │  • Mock data fallback for testing                                  │ │
│  └───────────────────────────┬────────────────────────────────────────┘ │
│                              ↓                                            │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  LAYER 4: Data Persistence (data_service.py)                       │ │
│  │  • Save daily_state (mood_index, volatility, trend)               │ │
│  │  • Save correlation_edges (market relationships)                   │ │
│  │  • Query historical data                                            │ │
│  └───────────────────────────┬────────────────────────────────────────┘ │
│                              ↓                                            │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  SCHEDULER (scheduler.py)                                           │ │
│  │  • Daily Analysis: 9:00 AM UTC (auto-fetch + analyze)             │ │
│  │  • Weekly Cleanup: Sunday 2:00 AM (delete old data)               │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                   DATABASE (PostgreSQL:5432)                              │
│                                                                           │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌────────────────┐│
│  │  market_registry     │  │  daily_state         │  │ correlation_   ││
│  │  ─────────────────   │  │  ─────────────────   │  │ edges          ││
│  │  • id (PK)           │←─│  • market_id (FK)    │  │ ──────────     ││
│  │  • name              │  │  • date              │  │ • source_id(FK)││
│  │  • latitude          │  │  • mood_index        │  │ • target_id(FK)││
│  │  • longitude         │  │  • volatility_30d    │  │ • correlation_ ││
│  │  • market_group      │  │  • trend_strength    │  │   value        ││
│  │  • country           │  │  • updated_at        │  │ • date         ││
│  │                      │  │                      │  │ • updated_at   ││
│  │  79 markets          │  │  Time-series data    │  │ Graph data     ││
│  └──────────────────────┘  └──────────────────────┘  └────────────────┘│
└──────────────────────────────────────────────────────────────────────────┘

                                 ↓
┌──────────────────────────────────────────────────────────────────────────┐
│               EXTERNAL DATA SOURCE (Yahoo Finance API)                    │
│  • Real-time stock prices (OHLCV data)                                   │
│  • 30-day historical data for volatility calculation                     │
│  • 79 global market indices                                              │
└──────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Example

When you trigger an analysis (`POST /api/process/analyze`):

1. **Process Layer** → Receives request, starts pipeline
2. **Adapter Layer** → Fetches data from Yahoo Finance (79 markets)
3. **Analytics Layer** → Calculates mood indexes, volatilities, correlations
4. **Data Service Layer** → Saves 79 daily_state records + correlation_edges
5. **Database** → Stores results with timestamps
6. **API Response** → Returns summary to client

## Quick Start

### 1. Start the Project

```bash
docker compose up -d
```

Wait a bit until the database is healthy:
```
marketmind-postgres: ... healthy
```

Then you can query the data:
```bash
curl http://localhost/api/data/markets
```

If you have `jq` installed, you can format it nicely:
```bash
curl http://localhost/api/data/markets | jq
```

### 2. Check the API Docs

Open in browser: `http://localhost/apidocs`

You'll see all the endpoints and can test them directly in the browser.

## Markets We Track

We now track **79 global stock market indices** across 6 continents:

- 🌎 **North America** (10): S&P 500, Dow Jones, Nasdaq, Russell 2000, TSX, IPC Mexico, etc.
- 🌍 **Europe** (26): FTSE 100, DAX, CAC 40, FTSE MIB, IBEX 35, SMI, STOXX 50, etc.
- 🌏 **Asia-Pacific** (25): Nikkei 225, Shanghai Composite, Hang Seng, KOSPI, TAIEX, Sensex, ASX 200, etc.
- 🌎 **Latin America** (8): Bovespa, Merval, IPSA Chile, COLCAP Colombia, etc.
- 🌍 **Middle East** (6): Tel Aviv 125, TASI Saudi Arabia, ADX/DFM UAE, etc.
- 🌍 **Africa** (4): JSE South Africa, EGX Egypt, MASI Morocco

**Market Classification**:
- **DM (Developed Markets)**: 42 markets (US, Europe, Japan, Australia, etc.)
- **EM (Emerging Markets)**: 37 markets (China, India, Brazil, Russia, etc.)

Total: **79 markets**.

## API Endpoints
Details is in the API docs,swagger, but here are the main ones:
```
GET  /api/data/markets                          Get all markets
GET  /api/data/markets/US_SPX                   Get one market
GET  /api/history/markets/US_SPX/timeseries     Get historical data (?days=10)
POST /api/history/compare                       Compare two markets
GET  /api/history/rankings                      Rankings (?metric=mood_index)
GET  /api/process/snapshot                      Current snapshot
POST /api/process/analyze                       Manually trigger analysis
```

## How We Calculate Stuff

**Mood Index** (ranges from -1 to +1):
- Stock goes up a lot → mood is good
- High volatility → mood is bad
- High trading volume → mood is good

Formula: `0.5 × daily_return - 0.3 × volatility + 0.2 × volume_score`

**Volatility**: Measured over 30 days

**Correlation**: Shows how markets move together (e.g., when Asia goes up, Europe usually goes up too)

## Automation

Runs at 9 AM UTC every day to fetch new data, and cleans up old data once a week.

## Testing

### Run End-to-End Test

This checks if the whole pipeline works (fetch data → analyze → save):

```bash
cd backend
python tests/test_e2e_pipeline.py
```

Output looks like:
```
✓ All 15 markets fetched successfully
✓ Analysis completed, found N correlations
✓ Data saved successfully
```

### Run Integration Tests

Tests all the API endpoints to make sure they work:

```bash
cd backend
python tests/test_integration.py
```

### Run Performance Tests

See how fast the API is and how much it can handle:

```bash
cd backend
python tests/test_performance.py
```

### Run Unit Tests

Test individual modules:

```bash
cd backend
python tests/test_adapter.py      # Data adapter
python tests/test_analytics.py    # Analysis algorithms
```

## Project Structure

```
backend/
├── app/                      # Main code
│   ├── api/                  # API routes
│   ├── services/             # Business logic
│   └── models/               # Database models
├── tests/                    # Test code
│   ├── test_e2e_pipeline.py
│   ├── test_integration.py
│   └── other tests...
└── requirements.txt          # Dependencies

docker/
├── Dockerfile.backend        # Container config
├── nginx.conf               # Gateway config
└── init.sql                 # Database setup
```

## Stop the Project

```bash
# Stop containers
docker compose down

# Stop and delete database data (start fresh)
docker compose down -v
```

## Requirements

- Docker & Docker Compose
- Internet connection (to fetch Yahoo Finance data)

## Development

```bash
# Start only the database
docker compose up postgres -d

# Run backend locally
cd backend
python -m flask run

# Auto-reload on code changes (need python-dotenv)
FLASK_ENV=development python -m flask run
```
