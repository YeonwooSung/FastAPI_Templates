# 🚀 Batch Ingestion API

A high-performance, scalable batch ingestion API designed for microservices architectures.
Built with FastAPI and PostgreSQL, optimized for handling massive write workloads through efficient batch processing and PostgreSQL COPY operations.

## ✨ Features

### 🔥 High-Performance Write Operations
- **PostgreSQL COPY**: 10-50x faster than traditional INSERT operations
- **Intelligent Batching**: Adaptive batch sizing based on memory usage and timing
- **Async Processing**: Built on FastAPI and asyncio for maximum concurrency
- **Connection Pooling**: Optimized database connection management

### 📊 Smart Batch Management
- **Time-based Flushing**: Automatic batch processing with configurable timeouts
- **Priority Queuing**: High-priority events (payments, critical operations) get precedence
- **Memory Management**: Automatic flush when memory thresholds are reached
- **Status Tracking**: Real-time batch processing status via Redis

### 🏗️ Scalability & Reliability
- **Partitioned Tables**: Monthly partitions for optimal query performance
- **Horizontal Scaling**: Kubernetes HPA support with custom metrics
- **Load Balancing**: Nginx-based traffic distribution
- **Health Checks**: Comprehensive health monitoring and metrics

## 🏛️ Architecture

```
┌─────────────────────┐
│  Microservices      │
│  (User, Order,      │
│   Payment, etc.)    │
└─────────┬───────────┘
          │ HTTP POST /v1/ingest/batch
          ▼
┌─────────────────────┐
│  Load Balancer      │
│  (Nginx)            │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐     ┌─────────────────┐
│  Ingestion API      │────▶│  Redis          │
│  (FastAPI)          │     │  (Batch Status) │
│  - Batch Processing │     └─────────────────┘
│  - Validation       │
│  - Rate Limiting    │
└─────────┬───────────┘
          │ Batched COPY Operations
          ▼
┌─────────────────────┐
│  PostgreSQL 18      │
│  (Partitioned DB)   │
│  - Monthly Parts    │
│  - Optimized Indexes│
└─────────────────────┘
```

## ⚡ Performance

### Benchmarks
| Metric | Target | Excellent |
|--------|--------|-----------|
| Throughput | 10,000 events/sec | 50,000+ events/sec |
| Batch Latency (P95) | < 5 seconds | < 2 seconds |
| API Response (P95) | < 200ms | < 100ms |
| Error Rate | < 0.1% | < 0.01% |

### Optimizations
- **Batch Size**: 1,000-5,000 events per batch
- **Memory Limit**: 100MB per batch buffer
- **Timeout**: 30-second automatic flush
- **Partitioning**: Monthly table partitions
- **Indexing**: Composite indexes on (service_name, event_type, timestamp)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 18+
- Redis 7+
- Docker & Docker Compose (optional)

### Installation

#### Using Docker Compose (Recommended)
```bash
# Clone the repository
git clone https://github.com/your-username/batch-ingestion-api.git
cd batch-ingestion-api

# Start services
docker-compose up -d

# Check health
curl http://localhost:8000/v1/health
```

#### Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/ingestion_db"
export REDIS_URL="redis://localhost:6379"

# Run the application
python main.py
```

### Database Setup
```sql
-- Create database
CREATE DATABASE ingestion_db;

-- The application will automatically create partitioned tables
-- and indexes on startup
```

## 🔧 API Usage

### Basic Event Ingestion

```python
import aiohttp
import asyncio

async def send_events():
    events = [
        {
            "event_id": "evt_123",
            "service_name": "user-service",
            "event_type": "user_login",
            "payload": {
                "user_id": "user_456",
                "login_method": "email",
                "success": True
            },
            "metadata": {
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0..."
            }
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/v1/ingest/batch",
            json={"events": events, "priority": 5}
        ) as response:
            result = await response.json()
            print(f"Batch ID: {result['batch_id']}")

asyncio.run(send_events())
```

### Using the Client Library

```python
from client_example import IngestionClient

async def main():
    async with IngestionClient("http://localhost:8000") as client:
        # Send batch
        response = await client.send_batch(
            events=events,
            batch_id="my_batch_001",
            priority=8  # High priority
        )
        
        # Check status
        status = await client.get_batch_status(response["batch_id"])
        print(f"Status: {status}")

asyncio.run(main())
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/ingest/batch` | Ingest batch of events |
| `GET` | `/v1/batch/{batch_id}/status` | Get batch processing status |
| `GET` | `/v1/health` | Health check |
| `GET` | `/v1/metrics` | API metrics and statistics |

### Event Schema

```json
{
  "events": [
    {
      "event_id": "string",           // Unique event identifier
      "service_name": "string",       // Source microservice
      "event_type": "string",         // Event type/category
      "payload": {},                  // Event data (JSON object)
      "timestamp": "2024-01-01T00:00:00Z",  // ISO timestamp (optional)
      "metadata": {}                  // Additional metadata (optional)
    }
  ],
  "batch_id": "string",              // Optional batch identifier
  "priority": 5                      // Priority 0-10 (default: 0)
}
```

## 🐳 Deployment

### Docker Compose
```bash
# Production deployment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Kubernetes
```bash
# Apply configurations
kubectl apply -f k8s-deployment.yaml

# Check status
kubectl get pods -l app=ingestion-api
kubectl get hpa ingestion-api-hpa
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `BATCH_SIZE` | Events per batch | 1000 |
| `BATCH_TIMEOUT_SECONDS` | Batch flush timeout | 30 |
| `DB_POOL_MIN_SIZE` | Min DB connections | 5 |
| `DB_POOL_MAX_SIZE` | Max DB connections | 20 |
| `MAX_BATCH_MEMORY_MB` | Memory limit per batch | 100 |

## ⚙️ Configuration

### PostgreSQL Optimization
```sql
-- Recommended postgresql.conf settings
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 128MB
work_mem = 32MB
wal_buffers = 16MB
checkpoint_completion_target = 0.9
random_page_cost = 1.1
effective_io_concurrency = 200
```

### Application Configuration
```python
# settings.py
class Settings(BaseSettings):
    # Database
    database_url: str
    db_pool_min_size: int = 5
    db_pool_max_size: int = 20
    
    # Batch processing
    batch_size: int = 1000
    batch_timeout_seconds: int = 30
    max_batch_memory_mb: int = 100
    
    # Redis
    redis_url: str
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/v1/health
```

### Metrics Endpoint
```bash
curl http://localhost:8000/v1/metrics
```

### Key Metrics to Monitor
- **Throughput**: Events processed per second
- **Latency**: Batch processing time (P50, P95, P99)
- **Error Rate**: Failed batches percentage
- **Queue Size**: Pending batches count
- **Database Performance**: Connection pool usage, query times
- **System Resources**: CPU, memory, disk I/O

### Prometheus Integration
```yaml
# Add to your prometheus.yml
scrape_configs:
  - job_name: 'ingestion-api'
    static_configs:
      - targets: ['ingestion-api:8000']
    metrics_path: '/v1/metrics'
```

### Grafana Dashboard
Key visualizations:
- Events ingestion rate over time
- Batch processing latency distribution
- Database connection pool status
- Error rate and failed batches
- System resource utilization

## 🧪 Testing

### Unit Tests
```bash
pytest tests/unit/
```

### Integration Tests
```bash
pytest tests/integration/
```

### Load Testing
```bash
# Using the provided load test script
python load_test.py

# Or with artillery
artillery run load-test.yml
```

### Performance Testing
```bash
# Test with 10K events/sec for 5 minutes
python performance_test.py --rate 10000 --duration 300
```

## 🛠️ Development

### Setting Up Development Environment
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run in development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Code Quality
```bash
# Format code
black .
isort .

# Lint
flake8 .
mypy .

# Security check
bandit -r .
```

### Database Migrations
```bash
# Create new partition (automated in production)
python manage.py create_partition --month 2024-02

# Cleanup old partitions
python manage.py cleanup_partitions --older-than 3months
```
