from flask import Blueprint, jsonify, current_app, request, render_template
from wakeonlan import send_magic_packet
import logging
import os
import requests
import re
import urllib3
import warnings

status_bp = Blueprint("status", __name__)

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

    return render_template("loading.html", attempts=current_app.config["ATTEMPTS"])

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
    logger = logging.getLogger(__name__)

    # Get MAC address and URL from environment variables
    mac_address = os.getenv("MAC_ADDRESS")
    url = os.getenv("URL")
    
    current_app.config["ATTEMPTS"] += 1
    
    if current_app.config["TESTING"]:
        logger.info(f"Testing: Not sending magic packet, just validating MAC address: {mac_address}")
        validate_mac_address(mac_address)
    else:
        logger.info(f"Sending magic packet to {mac_address}")
        send_magic_packet(mac_address)

    if not current_app.debug:
        logger = logging.getLogger(__name__)
        logger.info(f"Sending magic packet to {mac_address}")
        send_magic_packet(mac_address)
        
    if check_url_status(url):
        status = "available"
    elif current_app.config["ATTEMPTS"] >= 10:
        status = "error"
    else:
        status = "unavailable"
    
    return jsonify(
        {
            "status": status,
            "attempts": current_app.config["ATTEMPTS"],
            "url": url
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
    
    # Suppress only the single InsecureRequestWarning from urllib3 needed for this request.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)

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
    return f"App debug mode is {'on' if current_app.debug else 'off'}"

def validate_mac_address(mac_address: str) -> None:
    """
    Validate the MAC address.
    
    Args:
        mac_address (str): The MAC address to validate.
    
    Raises:
        ValueError: If the MAC address is invalid.
    """
    logger = logging.getLogger(__name__)
    if not mac_address or not re.match(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$", mac_address):
        logger.error("Invalid or missing MAC_ADDRESS environment variable: {mac_address}")
        raise ValueError("Invalid or missing MAC_ADDRESS environment variable: {mac_address}")