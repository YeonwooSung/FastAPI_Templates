# Example for using ORM in Python with FastAPI and SQLAlchemy

## Features

This repo contains example code for following points,

- ORM Models.
- Creating a connection pool with the database.
- Auto migrate the models to create the desired tables automatically in the database (using [Alembic](https://alembic.sqlalchemy.org/en/latest/)).
- Creating FastAPI request models (schema).
- Example code for CRUD operations.
- Logging
- Request ID Middleware
- Request Logging Middleware
- Reading configuration from environment
- Samples for Dockerfile and docker-compose files

## Run locally

### API Service

Follow these steps to run the API service locally,
At the repository root, execute the following commands.

- Get dependencies.
`pip install -r requirements.txt`
- Set the environment variables - use the sample .env file provided in the repository.
- Edit the `sqlalchemy.url` config in the `alembic.ini` file to point it to your Postgres instance.
- Run the command `alembic upgrade head` to create the necessary tables.
- Execute the `uvicorn main:app --port {port number} --reload` command to start the service.

> Note: This assumes you already have a database instanse running. If not, use the following guide to run both API service and a database instance in Docker.

## Running in Docker
- Running in Docker is very simple, the repo includes a `docker-compose.yaml` file.
- At the repository root, execute `docker-compose up` command to deploy the Postgres database instance and the API service.

> FastAPI comes with built-in swagger UI. To play around with these example APIs, you can open the URL, `http://localhost:{port}/docs`
