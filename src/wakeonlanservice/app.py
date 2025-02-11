# Import the create_app function
from wakeonlanservice import create_app

# Create the Flask application instance
app = create_app()

if __name__ == "__main__":
    # Run the Flask application
    app.run()