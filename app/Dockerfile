FROM python:2.7.14-alpine

RUN pip install beautifulsoup4 requests mechanize html2text slacker websocket-client

RUN mkdir -p /glory_wall
COPY ./app /glory_wall

WORKDIR /glory_wall
