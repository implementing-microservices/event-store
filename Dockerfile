FROM python:3.7-alpine
MAINTAINER Irakli Nadareishvili

COPY . /app
WORKDIR /app

RUN apk upgrade --update \
 && apk add --no-cache build-base \
 && apk add bash \
 && pip install -r requirements.txt \
 && apk del build-base # reduce size \
 && apk add make


CMD ["gunicorn", "-b 0.0.0.0", "--reload", \
     "-w 4", "server:app"]