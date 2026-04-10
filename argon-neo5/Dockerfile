ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache \
    python3 \
    py3-pip \
    i2c-tools

RUN pip3 install --no-cache-dir --break-system-packages smbus2

COPY run.sh /
COPY argon_daemon.py /

RUN chmod a+x /run.sh

CMD ["/run.sh"]
