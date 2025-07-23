#!/usr/bin/with-contenv bashio

# Read configuration from Home Assistant's options.json
export API_KEY=$(bashio::config 'api_key')
export SUBDOMAIN=$(bashio::config 'subdomain')

# Check if required config is set
if [[ -z "$API_KEY" ]] || [[ -z "$SUBDOMAIN" ]]; then
    bashio::log.fatal "API Key and Subdomain are not configured. Please set them in the add-on configuration tab."
    exit 1
fi

# The internal URL to the Home Assistant API
export HA_URL="http://supervisor/core"

bashio::log.info "Starting Web UI on port 8099..."
# Start the Gunicorn server for the Flask UI in the background
gunicorn --workers 1 --bind 0.0.0.0:8099 web_ui:app &

bashio::log.info "Starting Tunnel Client..."
# Start the main tunnel client in the foreground
python3 -u tunnel_client.py