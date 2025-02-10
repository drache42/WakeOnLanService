import logging
from flask import Flask
import os
import re

# Import blueprints
from wakeonlanservice.blueprints.status import status_bp

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG if app.debug else logging.INFO)
logger = logging.getLogger(__name__)

# Print the current debug level
current_debug_level = logging.getLevelName(logger.getEffectiveLevel())
logger.info(f"Current debug level: {current_debug_level}")

# Check if the app is in debug mode based on an environment variable
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

# Register blueprints
app.register_blueprint(status_bp)

if __name__ == "__main__":
    app.run()