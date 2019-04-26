FROM ubuntu:18.04 as builder

RUN apt-get update \
    && apt-get install -y wget unzip

WORKDIR /usr/src/app

COPY . /usr/src/app
RUN ./scripts/load_templates.sh

COPY scripts/build_schemas.sh /runner/
COPY data-source /runner/data-source
RUN mkdir -p /runner/data/en
RUN ./build_schemas.sh

###############################################################################
# Second Stage
###############################################################################

FROM python:3.7-slim-stretch

EXPOSE 5000

RUN apt update && apt install -y libsnappy-dev build-essential

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

ENV GUNICORN_WORKERS 3

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pip install pipenv==2018.11.26

RUN pipenv install --deploy --system

COPY --from=builder /usr/src/app/ /usr/src/app

CMD ["sh", "docker-entrypoint.sh"]
