FROM python:2.7.14-alpine

RUN apk update && \
    apk add postgresql-dev gcc musl-dev

RUN pip install beautifulsoup4 requests mechanize html2text slacker websocket-client peewee psycopg2 chatterbot Jinja2

RUN mkdir -p /glory_wall
COPY ./source/ /glory_wall

WORKDIR /glory_wall
