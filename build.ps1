<#
.SYNOPSIS
    Build and optionally push and run a Docker image.

.DESCRIPTION
    This script builds a Docker image for the WakeOnLanService application.
    If the --build-only parameter is set, it only builds the image without pushing it to the Docker repository.
    If the --run parameter is set, it runs the Docker container after building and optionally pushing.

.PARAMETER BuildOnly
    If set, the script will only build the Docker image and not push it to the repository.

.PARAMETER Run
    If set, the script will run the Docker container after building and optionally pushing.

.EXAMPLE
    .\build.ps1
    Builds and pushes the Docker image.

.EXAMPLE
    .\build.ps1 -BuildOnly
    Only builds the Docker image without pushing it to the repository.

.EXAMPLE
    .\build.ps1 -Run
    Builds and runs the Docker container without pushing it to the repository.
#>

# Define parameters to check if the --build-only or --run switches are set
param (
    [switch]$BuildOnly,
    [switch]$Run
)

# Read the configuration file
$config = Get-Content -Path "debug.json" | ConvertFrom-Json
$url = $config.URL
$macAddress = $config.MAC_ADDRESS

# Build the Docker image
Write-Output "Building the Docker image..."
docker build -t drache42/wakeonlanservice:latest -f docker/Dockerfile .

# If the --build-only switch is set, exit after building the image
if ($BuildOnly) {
    Write-Output "Build only, not pushing to Docker repository."
    exit 0
}

# If the --run switch is set, run the Docker container after building the image
if ($Run) {
    Write-Output "Running the Docker container..."
    docker run -it --rm -p 4200:4200 -e URL=$url -e MAC_ADDRESS=$macAddress drache42/wakeonlanservice:latest
    exit 0
}

# Log in to Docker
Write-Output "Logging in to Docker..."
docker login

# Push the Docker image to the repository
Write-Output "Pushing the Docker image to the repository..."
docker push drache42/wakeonlanservice:latest