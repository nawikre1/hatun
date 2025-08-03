#!/usr/bin/with-contenv bashio

# This function is called when the script receives a stop signal
cleanup() {
    bashio::log.info "Received stop signal. Bringing down wg0 interface..."
    wg-quick down wg0
    bashio::log.info "wg0 interface has been brought down. Exiting."
    exit 0
}

# Trap SIGTERM and SIGINT to call the cleanup function
trap 'cleanup' SIGTERM SIGINT

API_KEY=$(bashio::config 'api_key')
if [[ -z "$API_KEY" ]]; then
    bashio::log.fatal "API Key is not configured."
    exit 1
fi

bashio::log.info "Fetching WireGuard configuration from server..."

# Bring down wg0 if it exists from a previous run
if ip link show wg0 &>/dev/null; then
    bashio::log.info "Bringing down existing wg0 interface..."
    # The '|| true' prevents the script from exiting if the interface was already down
    wg-quick down wg0 || true
fi

# Remove old configuration if it exists
if [[ -f /etc/wireguard/wg0.conf ]]; then
    bashio::log.info "Removing old WireGuard configuration file..."
    rm -f /etc/wireguard/wg0.conf
fi

# Get the config file content from the new endpoint
CONFIG_CONTENT=$(curl -G -s --data-urlencode "apiKey=${API_KEY}" "https://webfork.tech/api/v1/wireguard-config")

if [[ -z "$CONFIG_CONTENT" ]]; then
    bashio::log.fatal "Failed to get configuration from server. Response was empty."
    exit 1
fi

# Write the configuration to the correct location
mkdir -p /etc/wireguard
echo "${CONFIG_CONTENT}" > /etc/wireguard/wg0.conf

bashio::log.info "Configuration received. Starting WireGuard tunnel..."

# Use wg-quick to bring up the interface
wg-quick up wg0

bashio::log.info "Tunnel is up. The add-on will now wait for a stop signal."

# This loop keeps the script running.
# 'wait' will pause the script until the backgrounded 'sleep' is interrupted by the trap.
while true; do
    sleep 3600 &
    wait $!
done