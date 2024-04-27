# Async Queue with Redis

Use Redis to create an async queue.

## Docker compose

- MySQL for DB
- Sidekiq to monitoring the redis queue
- Redis for async message queue (pub/sub)

```bash
docker-compose up
```
