# PostgreSQL과 Redis만 Docker로 실행
docker-compose up -d postgres redis

# 로컬에서 애플리케이션 실행
export POSTGRES_HOST=localhost
export REDIS_HOST=localhost
export PYTHONPATH=.
uvicorn app.main:app --host 0.0.0.0 --port 8000
