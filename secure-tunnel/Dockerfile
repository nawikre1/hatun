# ha-tunnel-addon/Dockerfile
ARG BUILD_FROM=python:3.11-slim-buster

FROM ${BUILD_FROM}

# Install system dependencies
# jq is used in run.sh to parse the config file
RUN apt-get update && apt-get install -y --no-install-recommends \
    jq

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