FROM python:3.12.3-alpine3.19


# Metadata
LABEL maintainer="vfabi <vaad.fabi@gmail.com>"
ARG TARGETARCH
ARG APP_NAME=smtp-to-telegram
ARG APP_VERSION=1.0.0
ENV APP_NAME=${APP_NAME}
ENV APP_VERSION=${APP_VERSION}
ENV PYTHONUNBUFFERED=1


# Common
ADD app /app
RUN apk add --no-cache git
RUN pip3 install --upgrade pip && pip3 install -r /app/requirements.txt


# Entrypoint
RUN chmod -R 755 /app
WORKDIR /app
ENTRYPOINT ["python3", "/app/main.py"]