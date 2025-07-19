import asyncio
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
import redis

from ..utils.logging import logger
from ..infra.database.manager import DatabaseManager
from ..infra.database.settings import settings
from ..models.base import EventData


class BatchProcessor:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.redis_client = redis.from_url(settings.redis_url)
        self.active_batches: Dict[str, List[EventData]] = {}
        self.batch_timers: Dict[str, asyncio.Task] = {}
    
    async def add_to_batch(self, events: List[EventData], batch_id: str) -> None:
        """Add events to a batch for processing"""
        if batch_id not in self.active_batches:
            self.active_batches[batch_id] = []
        
        self.active_batches[batch_id].extend(events)
        
        # Start timer for this batch if not already started
        if batch_id not in self.batch_timers:
            self.batch_timers[batch_id] = asyncio.create_task(
                self._batch_timer(batch_id)
            )
        
        # Check if batch is ready for processing
        if len(self.active_batches[batch_id]) >= settings.batch_size:
            await self._process_batch(batch_id)
    
    async def _batch_timer(self, batch_id: str) -> None:
        """Timer to process batch after timeout"""
        try:
            await asyncio.sleep(settings.batch_timeout_seconds)
            if batch_id in self.active_batches and self.active_batches[batch_id]:
                await self._process_batch(batch_id)
        except asyncio.CancelledError:
            pass  # Timer was cancelled because batch was processed
    
    async def _process_batch(self, batch_id: str) -> None:
        """Process and insert batch to database"""
        if batch_id not in self.active_batches:
            return
        
        events = self.active_batches.pop(batch_id)
        
        # Cancel timer if exists
        if batch_id in self.batch_timers:
            self.batch_timers[batch_id].cancel()
            del self.batch_timers[batch_id]
        
        if not events:
            return
        
        try:
            # Insert events to database
            inserted_count = await self.db_manager.batch_insert_events(events)
            
            # Update Redis with processing status
            await self._update_batch_status(
                batch_id, 
                "completed", 
                {"inserted_count": inserted_count}
            )
            
            logger.info(
                "Batch processed successfully",
                batch_id=batch_id,
                event_count=len(events),
                inserted_count=inserted_count
            )
            
        except Exception as e:
            logger.error(
                "Failed to process batch",
                batch_id=batch_id,
                event_count=len(events),
                error=str(e)
            )
            
            # Update Redis with error status
            await self._update_batch_status(
                batch_id, 
                "failed", 
                {"error": str(e)}
            )
    
    async def _update_batch_status(
        self, 
        batch_id: str, 
        status: str, 
        details: Dict[str, Any]
    ) -> None:
        """Update batch processing status in Redis"""
        try:
            status_data = {
                "batch_id": batch_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details
            }
            
            # Store with 1 hour expiration
            self.redis_client.setex(
                f"batch_status:{batch_id}",
                3600,
                json.dumps(status_data)
            )
        except Exception as e:
            logger.warning("Failed to update batch status", error=str(e))
    
    async def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get batch processing status"""
        try:
            status_data = self.redis_client.get(f"batch_status:{batch_id}")
            if status_data:
                return json.loads(status_data)
        except Exception as e:
            logger.warning("Failed to get batch status", error=str(e))
        
        return None
