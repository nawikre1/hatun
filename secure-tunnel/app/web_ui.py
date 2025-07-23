# ha-tunnel-addon/app/web_ui.py
from flask import Flask, render_template, jsonify, request
import os

app = Flask(__name__)
STATUS_FILE = "/tmp/tunnel_status"

@app.route('/')
def index():
    """Serves the main status page."""
    # The base path for Ingress needs to be handled
    ingress_path = request.headers.get("X-Ingress-Path", "")
    return render_template('index.html', ingress_path=ingress_path)

@app.route('/status')
def status():
    """API endpoint for the frontend to fetch the current status."""
    try:
        with open(STATUS_FILE, "r") as f:
            current_status = f.read().strip()
    except FileNotFoundError:
        current_status = "Initializing..."
    
    return jsonify({
        "status": current_status,
        "configured_subdomain": os.getenv('SUBDOMAIN', 'Not Set')
    })

# This part is not strictly needed when using Gunicorn, but good for testing
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8099)