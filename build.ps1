<#
.SYNOPSIS
    Build and optionally push and run a Docker image.

.DESCRIPTION
    This script builds a Docker image for the WakeOnLanService application.
    If the -Run parameter is set, it runs the Docker container after building

.PARAMETER Run
    If set, the script will run the Docker container after building and optionally pushing.

.EXAMPLE
    .\build.ps1
    Only builds the Docker image without running

.EXAMPLE
    .\build.ps1 -Run
    Builds and runs the Docker container without pushing it to the repository.
#>

param (
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
docker build -t drache42/wakeonlanservice:local -f docker/Dockerfile .

# If the --build-only switch is set, exit after building the image
if ($BuildOnly) {
    exit 0
}

# If the --run switch is set, run the Docker container after building the image
if ($Run) {
    Write-Output "Running the Docker container..."
    docker run -it --rm -p 4200:4200 -e URL=$env:URL -e MAC_ADDRESS=$env:MAC_ADDRESS drache42/wakeonlanservice:local
    exit 0
}