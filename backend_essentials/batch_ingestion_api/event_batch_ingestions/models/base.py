from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class EventData(BaseModel):
    """Individual event data model"""
    event_id: str = Field(..., description="Unique event identifier")
    service_name: str = Field(..., description="Source microservice name")
    event_type: str = Field(..., description="Type of event")
    payload: Dict[str, Any] = Field(..., description="Event payload data")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_timestamp(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v


class BatchRequest(BaseModel):
    """Batch ingestion request model"""
    events: List[EventData] = Field(..., min_items=1, max_items=5000)
    batch_id: Optional[str] = Field(None, description="Optional batch identifier")
    priority: int = Field(default=0, ge=0, le=10, description="Processing priority")


class BatchResponse(BaseModel):
    """Batch ingestion response model"""
    batch_id: str
    accepted_count: int
    processing_status: str
    estimated_processing_time_seconds: int
