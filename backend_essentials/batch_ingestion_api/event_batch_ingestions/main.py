# requirements.txt
"""
fastapi==0.104.1
uvicorn==0.24.0
asyncpg==0.29.0
pydantic==2.5.0
pydantic-settings==2.1.0
redis==5.0.1
structlog==23.2.0
"""

from datetime import datetime
from typing import Dict, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks

from .constants.log_configs import LOG_CONFIG
from .infra.database.manager import DatabaseManager
from .infra.database.settings import settings
from .core.batch_processor import BatchProcessor
from .utils.logging import logger
from .models.base import BatchRequest, BatchResponse


# Global instances
db_manager = DatabaseManager()
batch_processor = BatchProcessor(db_manager)


# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db_manager.initialize()
    logger.info("Batch Ingestion API started")

    yield

    # Shutdown
    await db_manager.close()
    logger.info("Batch Ingestion API shutdown")


# FastAPI Application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="High-performance batch ingestion API for microservices data",
    lifespan=lifespan
)


# API Endpoints
@app.post("/v1/ingest/batch", response_model=BatchResponse)
async def ingest_batch(
    request: BatchRequest,
    background_tasks: BackgroundTasks
) -> BatchResponse:
    """
    Ingest a batch of events from microservices
    
    This endpoint accepts events and processes them in optimized batches
    using PostgreSQL COPY commands for maximum write performance.
    """
    batch_id = request.batch_id or f"batch_{datetime.utcnow().timestamp()}"
    
    try:
        # Add events to batch processor
        background_tasks.add_task(
            batch_processor.add_to_batch,
            request.events,
            batch_id
        )
        
        # Estimate processing time based on batch size and current load
        estimated_time = min(
            settings.batch_timeout_seconds,
            len(request.events) // 100 + 5
        )
        
        logger.info(
            "Batch ingestion request received",
            batch_id=batch_id,
            event_count=len(request.events),
            priority=request.priority
        )
        
        return BatchResponse(
            batch_id=batch_id,
            accepted_count=len(request.events),
            processing_status="accepted",
            estimated_processing_time_seconds=estimated_time
        )
        
    except Exception as e:
        logger.error("Failed to accept batch", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process batch")


@app.get("/v1/batch/{batch_id}/status")
async def get_batch_status(batch_id: str) -> Dict[str, Any]:
    """Get the processing status of a specific batch"""
    status = await batch_processor.get_batch_status(batch_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return status


@app.get("/v1/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    try:
        # Test database connection
        async with db_manager.pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/v1/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get API metrics and statistics"""
    try:
        async with db_manager.pool.acquire() as conn:
            # Get total event count
            total_events = await conn.fetchval(
                "SELECT COUNT(*) FROM events WHERE created_at > NOW() - INTERVAL '24 hours'"
            )
            
            # Get events by service
            service_stats = await conn.fetch("""
                SELECT service_name, COUNT(*) as event_count
                FROM events 
                WHERE created_at > NOW() - INTERVAL '24 hours'
                GROUP BY service_name
                ORDER BY event_count DESC
                LIMIT 10
            """)
        
        return {
            "total_events_24h": total_events,
            "active_batches": len(batch_processor.active_batches),
            "service_statistics": [dict(row) for row in service_stats],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=4,
        log_config=LOG_CONFIG
    )
