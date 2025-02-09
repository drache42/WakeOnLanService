# WakeOnLanService

## Build Instructions

### Building

Run `build.ps1`, `build.ps1 -BuildOnly` or `build.ps1 -Run`

#### Advanced

To build the Docker image for this application, navigate to the root directory of the project and run the following command:

```sh
docker build -t drache42/wakeonlanservice:latest -f docker/Dockerfile .
```

#### Running

To run the the project locally, run the following command:

```sh
docker run -it --rm -p 5000:5000 drache42/wakeonlanservice:latest
```

#### Pushing

To push to my private repo after the build command, run the following commands:

```sh
docker login
docker push drache42/wakeonlanservice:latest
```

## Development Instructions

To run the Flask app in development mode, follow these steps:

1. Ensure all dependencies are installed:

```sh
pip install -r requirements.txt
```

2. Set environment variables and run the Flask app:

```
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
$env:FLASK_DEBUG = "true"
flask run
```

Access the application: Open your web browser and navigate to http://127.0.0.1:5000/.

### Debug Mode
When running in debug mode, the application will not redirect to the target URL even if it becomes accessible. Instead, it will continue to render the loading page and display the number of attempts made to check the URL. This is useful for testing and debugging purposes.

To enable debug mode, set the FLASK_DEBUG environment variable to true as shown in the development instructions above. 