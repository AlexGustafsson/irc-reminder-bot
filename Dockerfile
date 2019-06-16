FROM python:3-alpine

ADD https://github.com/scrapinghub/dateparser/archive/v0.7.1.tar.gz dateparser
RUN apk update && apk add gcc libc-dev && easy_install dateparser && apk del gcc libc-dev

RUN mkdir -p /var/www && mkdir -p /var/data
COPY src /var/www/

ENV DATA_DIRECTORY="/var/data"

CMD ["python", "/var/www/index.py"]
