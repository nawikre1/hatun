# ha-tunnel-addon/app/tunnel_client.py
import asyncio
import json
import logging
import os
import time
import httpx
import websockets
import base64

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_KEY = os.getenv('API_KEY')
SUBDOMAIN = os.getenv('SUBDOMAIN')
SERVER_DOMAIN = "webfork.tech" # IMPORTANT: Change this to your Go server's domain
SERVER_URI = f"wss://{SERVER_DOMAIN}/connect"
HA_URL = os.getenv('HA_URL', 'http://supervisor/core')
STATUS_FILE = "/tmp/tunnel_status"

# --- Status Management ---
def update_status(status: str):
    """Writes the current connection status to a file for the UI to read."""
    try:
        with open(STATUS_FILE, "w") as f:
            f.write(status)
        logging.info(f"Status updated to: {status}")
    except Exception as e:
        logging.error(f"Failed to write status file: {e}")

# --- Main Client Logic ---
async def run_client():
    """Main function to run the WebSocket client with reconnection logic."""
    reconnect_delay = 5  # Initial delay in seconds

    while True:
        try:
            update_status(f"Connecting to {SERVER_URI}...")
            async with websockets.connect(SERVER_URI) as websocket:
                logging.info("Connection established. Authenticating...")
                
                # 1. Authenticate by sending the API key
                await websocket.send(API_KEY)
                
                # Check for immediate closure due to bad auth
                # This is a simplified check. The server closes with a code.
                try:
                    # Wait for a short time to see if the server closes the connection
                    await asyncio.wait_for(websocket.recv(), timeout=2.0)
                except asyncio.TimeoutError:
                    # No message received, assume auth was successful
                    logging.info("Authentication successful. Listening for requests...")
                    update_status(f"Connected as {SUBDOMAIN}.{SERVER_DOMAIN}")
                    reconnect_delay = 5  # Reset delay on successful connection

                # 2. Listen for incoming proxy requests
                async for message in websocket:
                    asyncio.create_task(handle_proxy_request(message, websocket))

        except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.InvalidStatus) as e:
            logging.error(f"Connection closed: {e}. Reconnecting in {reconnect_delay}s...")
            update_status(f"Disconnected. Reconnecting...")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}. Reconnecting in {reconnect_delay}s...")
            update_status(f"Error. Reconnecting...")
        
        await asyncio.sleep(reconnect_delay)
        reconnect_delay = min(reconnect_delay * 2, 60) # Exponential backoff up to 60s

async def handle_proxy_request(message, websocket):
    """Handles a single proxy request received from the server."""
    try:
        req_data = json.loads(message)
        req_id = req_data.get("id")
        request_body_bytes=base64.b64decode(req_data.get("body", ""))

        async with httpx.AsyncClient(base_url=HA_URL, http2=True) as client:
            # Prepare the request for Home Assistant
            headers = {k: v[0] for k, v in req_data.get("headers", {}).items() if k.lower() != 'host'}
            
            response = await client.request(
                method=req_data.get("method"),
                url=req_data.get("url"),
                headers=headers,
                content=request_body_bytes,
                timeout=30.0,
            )

            # Prepare the response to send back over the tunnel
            response_body_b64 = base64.b64encode(response.content).decode('ascii')
            resp_data = {
                "id": req_id,
                "status": response.status_code,
                "headers": dict(response.headers),
                "body": response_body_b64,
            }
            await websocket.send(json.dumps(resp_data))

    except Exception as e:
        logging.error(f"Error handling proxy request: {e}")
        # If something goes wrong, inform the server
        if 'req_id' in locals():
            error_resp = {
                "id": req_id,
                "status": 500,
                "error": f"Tunnel client error: {e}",
                "body": [],
                "headers": {},
            }
            await websocket.send(json.dumps(error_resp))

if __name__ == "__main__":
    if not API_KEY or not SUBDOMAIN:
        logging.fatal("API_KEY and SUBDOMAIN must be set as environment variables.")
    else:
        asyncio.run(run_client())