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

## Simple Projects

- [Movie API Server](./sample_projects/fastapi-movie-api/)
- [GeoIP Server](./sample_projects/geoip/)
- [Sentiment Analyzer](./sample_projects/sentiment_analyzer/)
- [Simple Web Scraping Server](./sample_projects/scrap/)

## Design Patterns

- [Decorator Pattern](./design_patterns/decorator/)
- [Factory Pattern](./design_patterns/factory/)
- [Observer Pattern](./design_patterns/observer/)
- [Singleton Pattern](./design_patterns/singleton/)
- [Strategy Pattern](./design_patterns/strategy/)
