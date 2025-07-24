#!/usr/bin/with-contenv bashio

# Get the API key from the add-on configuration
API_KEY=$(bashio::config 'api_key')

if [[ -z "$API_KEY" ]]; then
    bashio::log.fatal "API Key is not configured. Please set it in the add-on configuration tab and restart."
    exit 1
fi

bashio::log.info "Fetching configuration from server..."

# Use curl to get the configuration from your Go server
# The server will validate the key and subscription status
HTTP_CODE=$(curl -s -w '%{http_code}' \
    -o /tmp/frpc.ini \
    "https://webfork.tech/api/v1/frp-config?apiKey=${API_KEY}")

# Check the response code from the server
if [[ "$HTTP_CODE" -ne 200 ]]; then
    ERROR_MESSAGE=$(cat /tmp/frpc.ini)
    bashio::log.fatal "Failed to get configuration from server. Status: ${HTTP_CODE}. Message: ${ERROR_MESSAGE}"
    exit 1
fi

bashio::log.info "Configuration received successfully. Starting FRP client..."

# Execute the frp client with the downloaded configuration
/usr/bin/frpc -c /tmp/frpc.ini