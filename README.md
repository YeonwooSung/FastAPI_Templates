# FastAPI Template

The aim of this project is to provide various templates and examples for building a FastAPI WAS.

## Simple Templates

- Admin
    * [fastapi_ami_admin](http://atomi.gitee.io/fastapi_amis_admin/tutorials/basic/PageAdmin/)
        * [simple example](./ami_admin_example/simple_admin_example/main.py)
        * [FormAdmin example](./ami_admin_example/admin_form_example/main.py)
        * [ModelAdmin example](./ami_admin_example/admin_model_example/main.py)
- SQL DB
    * [Basic CRUD template with ORM, connection pool, and Singleton](./sql-db/fastapi-crud/)
    * [FastAPI with SQLAlchemy DB connection pools](./sql-db/FastApi-SqlAlchemy/)
    * [ORM with N+1 problem and solution](./sql-db/simple_orm_example/)
    * [ORM example with alembic for DB migration](./sql-db/orm-example-with-alembic/)
- [Simple Dependency Injection](./simple_dependency_injection/)
- FastAPI advanced practices
    * [FastAPI Custom Exception Handlers And Logs](./basic-functionality/fastapi-custom-exception-handlers-and-logs/)
    * [FastAPI Custom Logging Middleware](./basic-functionality/simple-logging-middleware/)
    * [FastAPI with circuit breaker for external API service](./basic-functionality/simple-circuit-breaker/)
    * WebSocket
        * [FastAPI WebSocket with PubSub on Redis Queue](./basic-functionality/redis_pubsub_websocket/)
    * Session
        * [Simple Session Server](./basic-functionality/simple-session-server/)
        * [Redis Session Server](./basic-functionality/redis_session_server/)

## Backend Essentials

Let's learn essential stuffs for backend development.

- [Caching on Redis with Postgres Async Repository](./backend_essentials/fastapi_cache/)
- [Circuit Breaker](./backend-essentials/circuit-breaker/)
- [Redis Failover](./backend_essentials/redis_failover/)
- [Service Discovery with Zookeeper](./backend_essentials/service_discovery/)

## Simple Projects

- [Movie API Server](./sample_projects/fastapi-movie-api/)
- [GeoIP Server](./sample_projects/geoip/)
- [Sentiment Analyzer](./sample_projects/sentiment_analyzer/)
- [Simple Web Scraping Server](./sample_projects/scrap/)
- [Simple pet care service (use scylladb as backend)](./sample_projects/care_pet)

## Design Patterns

- [Decorator Pattern](./design_patterns/decorator/)
- [Factory Pattern](./design_patterns/factory/)
- [Observer Pattern](./design_patterns/observer/)
- [Singleton Pattern](./design_patterns/singleton/)
- [Strategy Pattern](./design_patterns/strategy/)

## Tips

References: [zhanymkanov/fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices)

- FastAPI's sync operations runs in threadpool
    - The size of the threadpool is 40, so if you exceed that number, sync operations might be blocked
    - If you want to optimize CPU intensive tasks you should send them to workers in another process.

To learn more about best practices of authentication & permissions please refer [here](https://github.com/zhanymkanov/fastapi-best-practices/issues/4)

### DB

#### Set DB keys naming conventions

Explicitly setting the indexes' namings according to your database's convention is preferable over sqlalchemy's.

```python
from sqlalchemy import MetaData

POSTGRES_INDEXES_NAMING_CONVENTION = {
    "ix": "%(column_0_label)s_idx",
    "uq": "%(table_name)s_%(column_0_name)s_key",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "pk": "%(table_name)s_pkey",
}
metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)
```

#### SQL-first. Pydantic-second

- Usually, database handles data processing much faster and cleaner than CPython will ever do.
- It's preferable to do all the complex joins and simple data manipulations with SQL.
- It's preferable to aggregate JSONs in DB for responses with nested objects.

```python
# src.posts.service
from typing import Any

from pydantic import UUID4
from sqlalchemy import desc, func, select, text
from sqlalchemy.sql.functions import coalesce

from src.database import database, posts, profiles, post_review, products

async def get_posts(
    creator_id: UUID4, *, limit: int = 10, offset: int = 0
) -> list[dict[str, Any]]: 
    select_query = (
        select(
            (
                posts.c.id,
                posts.c.slug,
                posts.c.title,
                func.json_build_object(
                   text("'id', profiles.id"),
                   text("'first_name', profiles.first_name"),
                   text("'last_name', profiles.last_name"),
                   text("'username', profiles.username"),
                ).label("creator"),
            )
        )
        .select_from(posts.join(profiles, posts.c.owner_id == profiles.c.id))
        .where(posts.c.owner_id == creator_id)
        .limit(limit)
        .offset(offset)
        .group_by(
            posts.c.id,
            posts.c.type,
            posts.c.slug,
            posts.c.title,
            profiles.c.id,
            profiles.c.first_name,
            profiles.c.last_name,
            profiles.c.username,
            profiles.c.avatar,
        )
        .order_by(
            desc(coalesce(posts.c.updated_at, posts.c.published_at, posts.c.created_at))
        )
    )
    
    return await database.fetch_all(select_query)

# src.posts.schemas
from typing import Any

from pydantic import BaseModel, UUID4

   
class Creator(BaseModel):
    id: UUID4
    first_name: str
    last_name: str
    username: str


class Post(BaseModel):
    id: UUID4
    slug: str
    title: str
    creator: Creator

    
# src.posts.router
from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/creators/{creator_id}/posts", response_model=list[Post])
async def get_creator_posts(creator: dict[str, Any] = Depends(valid_creator_id)):
   posts = await service.get_posts(creator["id"])

   return posts
```
