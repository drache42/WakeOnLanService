# Import the create_app function
from wakeonlanservice import create_app
import os

# Create the Flask application instance with a secret key for sessions
app = create_app({
    "SECRET_KEY": os.environ.get("SECRET_KEY", os.urandom(24))
})

if __name__ == "__main__":
    # Run the Flask application
    app.run()