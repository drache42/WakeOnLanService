import logging
from flask import Flask
import os
import re
from wakeonlanservice.logging_config import setup_logging

# Import blueprints
from wakeonlanservice.blueprints.status import status_bp

def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: The Flask application instance.
    """
    app = Flask(__name__)

    # Set up logging
    setup_logging(app.debug)

    # Validate environment variables
    validate_env_variables()

    # Register blueprints
    app.register_blueprint(status_bp)

    logger = logging.getLogger(__name__)
    logger.info("App created successfully")

    return app

def validate_env_variables() -> None:
    """
    Validate the required environment variables.
    
    Raises:
        ValueError: If any required environment variable is missing or invalid.
    """
    logger = logging.getLogger(__name__)

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

# Create the Flask application instance
app = create_app()

if __name__ == "__main__":
    # Run the Flask application
    app.run()