ARG BUILD_FROM=ghcr.io/hassio-addons/base:18.0.3

FROM ${BUILD_FROM}

RUN apk add --no-cache wget tar

ARG FRP_VERSION="0.59.0"
ARG TARGETARCH

RUN set -ex; \
    if [ "${TARGETARCH}" = "amd64" ]; then FRP_ARCH="amd64"; \
    elif [ "${TARGETARCH}" = "armv7" ]; then FRP_ARCH="arm"; \
    elif [ "${TARGETARCH}" = "aarch64" ]; then FRP_ARCH="arm64"; \
    else echo "Unsupported architecture: ${TARGETARCH}"; exit 1; fi; \
    wget "https://github.com/fatedier/frp/releases/download/v${FRP_VERSION}/frp_${FRP_VERSION}_linux_${FRP_ARCH}.tar.gz" -O /tmp/frp.tar.gz; \
    tar -zxvf /tmp/frp.tar.gz -C /tmp; \
    mv "/tmp/frp_${FRP_VERSION}_linux_${FRP_ARCH}/frpc" /usr/bin/frpc; \
    chmod +x /usr/bin/frpc; \
    rm -rf /tmp/*

COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]