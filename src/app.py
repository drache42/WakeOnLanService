import logging
from flask import Flask, jsonify, render_template, request
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
    """
    Logs information about each incoming request.
    This function is executed before each request is processed.
    Logs the HTTP method and the requested URL.
    """
    logger.info(f"Received {request.method} request for {request.url}")

@app.route("/check_url")
def check_url_status():
    """
    Endpoint to check the status of the URL.
    Increments the attempt counter and checks the URL status.
    If not in debug mode, sends a magic packet to the MAC address.
    Returns a JSON response with the status, number of attempts, and the URL.
    
    Status can be:
    - "available": The URL is reachable.
    - "debug": The application is in debug mode and less than 5 attempts have been made.
    - "error": The URL is not reachable after 10 attempts.
    - "unavailable": The URL is not reachable but less than 10 attempts have been made.
    """
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
    """
    Helper function to check if the URL is reachable.
    Returns True if the URL returns a 200 status code, False otherwise.
    """
    try:
        response = requests.get(url, timeout=5, verify=False)
        if response.status_code == 200:
            return True
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
    return False

@app.route("/")
def index():
    """
    Index route that resets the attempt counter and renders the loading page.
    """
    global attempts
    attempts = 0

    return render_template("loading.html", attempts=attempts)

@app.route("/debug-status")
def debug_status():
    """
    Route to check the debug status of the application.
    Returns a string indicating whether the app and environment variable debug modes are on or off.
    """
    return f"App debug mode is {'on' if app.debug else 'off'}, Environment variable debug mode is {'on' if DEBUG_MODE else 'off'}"

if __name__ == "__main__":
    app.run(debug=DEBUG_MODE)