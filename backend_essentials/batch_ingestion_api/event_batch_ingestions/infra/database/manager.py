import asyncpg
from typing import List, Optional
from datetime import datetime, timedelta
import csv
import io
import json

from .settings import settings
from ...models.base import EventData
from ...utils.logging import logger


class DatabaseManager:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def initialize(self):
        """Initialize database connection pool"""
        self.pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=settings.db_pool_min_size,
            max_size=settings.db_pool_max_size,
            command_timeout=60
        )
        
        # Create partitioned table if not exists
        await self._create_partitioned_tables()
        
        logger.info("Database pool initialized")

    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")

    async def _create_partitioned_tables(self):
        """Create partitioned tables for efficient data storage"""
        async with self.pool.acquire() as conn:
            # Main partitioned table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id BIGSERIAL,
                    event_id VARCHAR(255) NOT NULL,
                    service_name VARCHAR(100) NOT NULL,
                    event_type VARCHAR(100) NOT NULL,
                    payload JSONB NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    PRIMARY KEY (id, timestamp)
                ) PARTITION BY RANGE (timestamp);
            """)
            
            # Create partitions for current and next month
            current_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = current_date + timedelta(days=32)
            next_month = next_month.replace(day=1)
            
            for i in range(3):  # Create 3 months of partitions
                partition_start = current_date + timedelta(days=32 * i)
                partition_start = partition_start.replace(day=1)
                partition_end = partition_start + timedelta(days=32)
                partition_end = partition_end.replace(day=1)
                
                partition_name = f"events_{partition_start.strftime('%Y_%m')}"
                
                await conn.execute(f"""
                    CREATE TABLE IF NOT EXISTS {partition_name} 
                    PARTITION OF events 
                    FOR VALUES FROM ('{partition_start}') TO ('{partition_end}');
                """)
                
                # Create indexes on partitions
                await conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{partition_name}_service_type_time
                    ON {partition_name} (service_name, event_type, timestamp);
                """)
                
                await conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{partition_name}_event_id
                    ON {partition_name} (event_id);
                """)
    
    async def batch_insert_events(self, events: List[EventData]) -> int:
        """Efficiently insert events using COPY command"""
        if not events:
            return 0
        
        # Prepare CSV data in memory
        csv_buffer = io.StringIO()
        csv_writer = csv.writer(csv_buffer)
        
        for event in events:
            csv_writer.writerow([
                event.event_id,
                event.service_name,
                event.event_type,
                json.dumps(event.payload),
                event.timestamp.isoformat(),
                json.dumps(event.metadata)
            ])
        
        csv_data = csv_buffer.getvalue()
        csv_buffer.close()
        
        # Use COPY for bulk insert
        async with self.pool.acquire() as conn:
            try:
                copy_result = await conn.copy_to_table(
                    'events',
                    source=csv_data,
                    columns=[
                        'event_id', 'service_name', 'event_type', 
                        'payload', 'timestamp', 'metadata'
                    ],
                    format='csv'
                )
                
                # Extract number of inserted rows from copy result
                inserted_count = int(copy_result.split()[1])
                
                logger.info(
                    "Batch inserted events",
                    inserted_count=inserted_count,
                    total_events=len(events)
                )
                
                return inserted_count
                
            except Exception as e:
                logger.error("Failed to batch insert events", error=str(e))
                raise
