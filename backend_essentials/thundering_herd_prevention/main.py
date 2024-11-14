import asyncio
import aioredis
from fastapi import FastAPI, HTTPException
from typing import Optional

app = FastAPI()
redis = None

REDIS_URL = "redis://localhost:6379"
TASK_TIMEOUT = 10  # seconds
EXPENSIVE_TASK_RESULT_TTL = 60  # seconds

async def expensive_operation(key: str) -> str:
    """Simulates a time-consuming operation."""
    await asyncio.sleep(5)  # Simulate delay
    return f"Processed result for {key}"

async def get_or_run_task(key: str) -> str:
    """Manages task execution with Redis to avoid thundering herd."""
    global redis

    # Check if the task is already running or completed
    task_status = await redis.get(key)
    if task_status:
        if task_status.decode("utf-8") == "processing":
            # Wait for the existing task to finish
            for _ in range(TASK_TIMEOUT):
                await asyncio.sleep(1)
                task_status = await redis.get(key)
                if task_status and task_status.decode("utf-8") != "processing":
                    return task_status.decode("utf-8")
            raise HTTPException(status_code=500, detail="Task timeout")

        # If result exists in cache, return it
        return task_status.decode("utf-8")

    try:
        # Mark task as processing in Redis
        await redis.set(key, "processing", ex=TASK_TIMEOUT)

        # Run the expensive task
        result = await expensive_operation(key)

        # Cache the result in Redis
        await redis.set(key, result, ex=EXPENSIVE_TASK_RESULT_TTL)
        return result
    finally:
        # Clean up processing marker if the task fails
        current_status = await redis.get(key)
        if current_status and current_status.decode("utf-8") == "processing":
            await redis.delete(key)

@app.on_event("startup")
async def startup():
    """Initialize Redis connection."""
    global redis
    redis = await aioredis.from_url(REDIS_URL)

@app.on_event("shutdown")
async def shutdown():
    """Close Redis connection."""
    global redis
    if redis:
        await redis.close()

@app.get("/compute/{key}")
async def compute(key: str):
    """Endpoint that computes or fetches the result."""
    result = await get_or_run_task(key)
    return {"key": key, "result": result}

