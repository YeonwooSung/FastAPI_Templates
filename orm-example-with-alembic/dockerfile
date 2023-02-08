FROM python:3.9

ENV APP_NAME fastapi-example

COPY . /api/src/${APP_NAME}
WORKDIR /api/src/${APP_NAME}

RUN pip install -r requirements.txt