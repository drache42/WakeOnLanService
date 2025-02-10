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

# Function to read .env file and set environment variables
function Set-EnvVarsFromDotEnv {
    param (
        [string]$envFilePath
    )

    if (Test-Path $envFilePath) {
        $envFileContent = Get-Content $envFilePath
        foreach ($line in $envFileContent) {
            if ($line -match '^\s*#') { continue }  # Skip comments
            if ($line -match '^\s*$') { continue }  # Skip empty lines
            if ($line -match '^\s*([^=]+)\s*=\s*(.*)\s*$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                [System.Environment]::SetEnvironmentVariable($name, $value)
                Write-Output "Set environment variable: $name=$value"
            }
        }
    } else {
        Write-Output "The .env file does not exist at path: $envFilePath"
        exit 1
    }
}

# Read the .env file and set environment variables
Set-EnvVarsFromDotEnv -envFilePath ".env"

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
    docker run -it --rm -p 4200:4200 -e URL=$env:URL -e MAC_ADDRESS=$env:MAC_ADDRESS drache42/wakeonlanservice:latest
    exit 0
}

# Log in to Docker
Write-Output "Logging in to Docker..."
docker login

# Push the Docker image to the repository
Write-Output "Pushing the Docker image to the repository..."
docker push drache42/wakeonlanservice:latest