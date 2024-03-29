FROM python:3.11-alpine as requirements-stage

ENV VERSION 0.1.0

WORKDIR /tmp

RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev && \
    pip install poetry && \
    poetry config virtualenvs.create false

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11-alpine

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

WORKDIR /MovieAPI

COPY --from=requirements-stage /tmp/requirements.txt /MovieAPI/requirements.txt

RUN apk add --no-cache libffi openssl && \
    pip install --no-cache-dir --upgrade -r /MovieAPI/requirements.txt && \
    rm -rf /root/.cache && \
    rm -rf /var/cache/apk/*

COPY ./MovieAPI /MovieAPI/

# Change ownership of the app directory to the non-root user
RUN chown -R appuser:appuser /MovieAPI

USER appuser

WORKDIR /

ENV PORT=8000

CMD ["uvicorn", "MovieAPI.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]