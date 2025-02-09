import logging
from flask import Flask, jsonify, render_template, request, redirect, url_for
import requests
from wakeonlan import send_magic_packet
import os
import re

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG if os.getenv("FLASK_DEBUG", "false").lower() == "true" else logging.INFO)
logger = logging.getLogger(__name__)

# Check if the app is in debug mode based on an environment variable
DEBUG_MODE = os.getenv("FLASK_DEBUG", "false").lower() == "true"
logger.info(f"DEBUG_MODE: {DEBUG_MODE}")  # Log the debug mode status.
logger.info(f"App debug mode is {'on' if app.debug else 'off'}")

# Get MAC address and URL from environment variables
MAC_ADDRESS = os.getenv("MAC_ADDRESS")
URL = os.getenv("URL")

# Validate MAC address
if not MAC_ADDRESS or not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', MAC_ADDRESS):
    logger.error("Invalid or missing MAC_ADDRESS environment variable")
    raise ValueError("Invalid or missing MAC_ADDRESS environment variable")

# Validate URL
if not URL or not re.match(r'^(http|https)://', URL):
    logger.error("Invalid or missing URL environment variable")
    raise ValueError("Invalid or missing URL environment variable")

global attempts
attempts = 0

@app.before_request
def log_request_info():
    logger.info(f"Received {request.method} request for {request.url}")

@app.route("/check_url")
def check_url_status():
    global attempts
    attempts += 1
    
    if not DEBUG_MODE:
        logger.info(f"Sending magic packet to {MAC_ADDRESS}")
        send_magic_packet(MAC_ADDRESS)
        
    if app.debug:
        if attempts >= 5:
            status = "available"
        else:
            status = "debug"
    elif check_url(URL):
        status = "available"
    elif attempts >= 10:
        status = "error"
    else:
        status = "unavailable"
    
    return jsonify(
        {
            "status": status,
            "attempts": attempts,
            "url": URL
        })

def check_url(url):
    try:
        response = requests.get(url, timeout=5, verify=False)
        if response.status_code == 200:
            return True
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
    return False

@app.route("/")
def index():
    global attempts
    attempts = 0

    return render_template("loading.html", attempts=attempts)

@app.route("/app")
def app_page():
    url = request.args.get('url')
    return render_template("app.html", url=url)

@app.route("/debug-status")
def debug_status():
    return f"App debug mode is {'on' if app.debug else 'off'}, Environment variable debug mode is {'on' if DEBUG_MODE else 'off'}"

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE)