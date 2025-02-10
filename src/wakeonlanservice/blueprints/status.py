from flask import Blueprint, jsonify, current_app as app, request, render_template
from wakeonlan import send_magic_packet
import logging
import os
import requests

status_bp = Blueprint('status', __name__)

global attempts
attempts = 0

# Get MAC address and URL from environment variables
MAC_ADDRESS = os.getenv("MAC_ADDRESS")
URL = os.getenv("URL")

@status_bp.before_app_request
def log_request_info():
    """
    Logs information about each incoming request.
    This function is executed before each request is processed.
    Logs the HTTP method and the requested URL.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Received {request.method} request for {request.url}")

@status_bp.route("/")
def index():
    """
    Index route that resets the attempt counter and renders the loading page.
    
    Returns:
        str: Rendered HTML template for the loading page.
    """
    global attempts
    attempts = 0

    return render_template("loading.html", attempts=attempts)

@status_bp.route("/check_url")
def check_url():
    """
    Endpoint to check the status of the URL.
    Increments the attempt counter and checks the URL status.
    If not in debug mode, sends a magic packet to the MAC address.
    
    Returns:
        Response: JSON response with the status, number of attempts, and the URL.
    
    Status can be:
    - "available": The URL is reachable.
    - "error": The URL is not reachable after 10 attempts.
    - "unavailable": The URL is not reachable but less than 10 attempts have been made.
    """
    global attempts
    attempts += 1
    
    if not app.debug:
        logger = logging.getLogger(__name__)
        logger.info(f"Sending magic packet to {MAC_ADDRESS}")
        send_magic_packet(MAC_ADDRESS)
        
    if check_url_status(URL):
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

def check_url_status(url):
    """
    Helper function to check if the URL is reachable.
    
    Args:
        url (str): The URL to check.
    
    Returns:
        bool: True if the URL returns a 200 status code, False otherwise.
    
    Raises:
        requests.RequestException: If the request to the URL fails.
    """
    logger = logging.getLogger(__name__)
    logger.debug(f"Checking URL: {url}")
    try:
        response = requests.get(url, timeout=5, verify=False)
        if response.status_code == 200:
            return True
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
    return False

@status_bp.route("/debug-status")
def debug_status():
    """
    Route to check the debug status of the application.
    Returns a string indicating whether the app and environment variable debug modes are on or off.
    """
    return f"App debug mode is {'on' if app.debug else 'off'}"