# ha-tunnel-addon/Dockerfile
ARG BUILD_FROM=ghcr.io/hassio-addons/base-python:17.0.0

FROM ${BUILD_FROM}

# Install system dependencies
# jq is used in run.sh to parse the config file
RUN apk add --no-cache jq

# Set up the working directory
WORKDIR /app

# Copy and install python dependencies
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY app/ .

# Copy the run script and make it executable
COPY run.sh /
RUN chmod a+x /run.sh

# Start the application
CMD [ "/run.sh" ]