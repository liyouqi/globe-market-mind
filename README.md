# GlobeMarketMind - Global Market Sentiment Analysis

This is a simple Flask project that analyzes the mood/sentiment of 15 global stock markets. It automatically calculates a "mood index" for each market and shows how different markets are related to each other.

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

- **US** (3): SPX (S&P 500), IYY, CCMP
- **Europe** (3): STOXX, FTSE, SMI
- **Asia** (3): Nikkei, SSE, Sensex
- **Emerging Markets** (6): IBOV, KOSPI, MOEX, ASX, STI, MEXBOL

Total: 15 markets.

## API Endpoints

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
