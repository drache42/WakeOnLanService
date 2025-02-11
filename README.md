# WakeOnLanService

![Test Status](https://github.com/drache42/WakeOnLanService/actions/workflows/unit-tests.yml/badge.svg?branch=main)

## Build Instructions for Docker

### Building

Run `build.ps1` to build and push to docker

Run `build.ps1 -BuildOnly` to only build the dockerfile

Run `build.ps1 -Run` to build and run the container, without pushing

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

### Initial Set Up

1. Clone this repo

1. Create a virtual environment

   Python virtual environments allow you to install Python packages in a location isolated from the rest of your system instead of installing them system-wide. 
   You can learn more about virtual environments on the [Python.land website](https://python.land/virtual-environments/virtualenv)

1. Activate the virtual environment

1. Install Poetry

    Package management is handled via Poetry.
    If you don't have Poetry installed, you can install it by following the instructions on the [Poetry website](https://python-poetry.org/docs/#installation).

1. Install Dependencies

   `poetry install`

1. Set Up Environment Variables

   Create a `.env` file in the root directory of the project and add the necessary environment variabless:

   ```env
   FLASK_APP=src.app
   FLASK_ENV=development
   FLASK_DEBUG=1
   MAC_ADDRESS=your_mac_address_here
   URL=your_url_here
   ```

1. Run the Flask Application

   With the virtual environment activated and environment variables set, you can now run your Flask application:

   ```sh
   flask run --host=0.0.0.0 --port=5000
   ```

   Access the application by opening your web browser and navigating to http://127.0.0.1:5000/.

### Optional VSCode Set Up

If you want to use VSCode for development, create a `.vscode\launch.json`

```json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/src/wakeonlanservice/app.py",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src",
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "true",
                "URL": you_url_here,
                "MAC_ADDRESS": your_mac_address_here
            },
            "args": [],
            "jinja": true
        }
    ]
}
```
