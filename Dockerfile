FROM python:3.7.0a4-alpine3.7

# RUN apk update && apk add gcc musl-dev libffi-dev py-cairo cairo libxml2-dev libxslt-dev zlib-dev

RUN pip install beautifulsoup4 requests mechanize html2text slacker
# cairosvg==1.0.22 cairocffi cffi lxml

RUN mkdir -p /glory_wall
COPY ./app /glory_wall
COPY credentials.txt /glory_wall

COPY entrypoint.sh /usr/local/bin
RUN chmod +x /usr/local/bin/entrypoint.sh

WORKDIR /glory_wall

# CMD ["python", "summary.py"]
ENTRYPOINT ["entrypoint.sh"]
