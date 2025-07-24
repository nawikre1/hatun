ARG BUILD_FROM=ghcr.io/hassio-addons/base:18.0.3

FROM ${BUILD_FROM}

RUN apk add --no-cache wireguard-tools curl

COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]