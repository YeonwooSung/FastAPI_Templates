# Caching - Thundering Herd Prevention

The thundering herd problem occurs when a large number of processes or threads waiting for an event are awoken when that event occurs, but only one process is able to handle the event.

This happens when many clients access to same resource.
When so many requests try to access some cache value and the target value is not cached yet, users will face with the thundering herd problem.

To avoid this, we need to block all non-first requests till the target value is cached successfully (or the cache is updated successfully).

## Running instruction

Run redis with docker:
```bash
docker run --name redis -d -p 6379:6379 redis
```

Then run the fastapi app:
```bash
uvicorn main:app --reload
```

Next, request data with `curl`:
```bash
curl http://127.0.0.1:8000/compute/key1
```

