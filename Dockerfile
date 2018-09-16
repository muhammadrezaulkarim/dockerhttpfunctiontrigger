FROM python:3.6.6-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app
COPY functiontrigger /usr/src/app/functiontrigger

RUN apk add --no-cache \
        bash \
        ca-certificates \
        g++ \
        git \
        libressl \
        libressl-dev \
        linux-headers \
        make \
        musl-dev \
        zlib-dev  \
        tar \
        autoconf \
        automake \
        gcc \
        git \
        libtool \
        make \
        musl-dev \
        curl \
      
  && pip install --no-cache-dir -r requirements.txt \
  && pip install kafka-python \
  && pip install cffi
  && pip install multiprocessing-logging \
  && pip install docker[tls] \
  && rm -rf /var/cache/apk/* 

CMD ["/usr/bin/python", "functiontrigger/functiontrigger.py"]
