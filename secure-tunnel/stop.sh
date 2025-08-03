#!/usr/bin/with-contenv bashio

# Bring down wg0 if it exists
if ip link show wg0 &>/dev/null; then
    bashio::log.info "Bringing down existing wg0 interface (stop/uninstall)..."
    wg-quick down wg0 || bashio::log.warning "wg0 was not up or failed to bring down."
fi

# Remove old configuration if it exists
if [[ -f /etc/wireguard/wg0.conf ]]; then
    bashio::log.info "Removing old WireGuard configuration file (stop/uninstall)..."
    rm -f /etc/wireguard/wg0.conf
fi

bashio::log.info "WireGuard cleanup complete."
