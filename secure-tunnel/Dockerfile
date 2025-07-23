ARG BUILD_FROM=python:3.11

FROM ${BUILD_FROM}

RUN apk add --no-cache jq

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]