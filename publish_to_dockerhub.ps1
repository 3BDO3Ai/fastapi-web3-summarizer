# PowerShell script for Windows users to publish Docker image to Docker Hub

# Configuration
$IMAGE_NAME = "web3-summarizer-api"
$VERSION = Get-Date -Format "yyyyMMddHHmm"

# Check if username is provided
if (-not $args[0]) {
    Write-Host "Error: Docker Hub username is required" -ForegroundColor Red
    Write-Host "Usage: .\publish_to_dockerhub.ps1 YOUR_DOCKERHUB_USERNAME"
    exit 1
}

$DOCKER_USERNAME = $args[0]
$FULL_IMAGE_NAME = "$DOCKER_USERNAME/$IMAGE_NAME"

Write-Host "Building Docker image: $FULL_IMAGE_NAME`:latest and $FULL_IMAGE_NAME`:$VERSION" -ForegroundColor Cyan

# Build the Docker image
docker build -t "$FULL_IMAGE_NAME`:latest" -t "$FULL_IMAGE_NAME`:$VERSION" .

# Log in to Docker Hub (will prompt for password if not already logged in)
Write-Host "Logging in to Docker Hub as $DOCKER_USERNAME" -ForegroundColor Cyan
docker login -u "$DOCKER_USERNAME"

# Push the images to Docker Hub
Write-Host "Pushing images to Docker Hub" -ForegroundColor Cyan
docker push "$FULL_IMAGE_NAME`:latest"
docker push "$FULL_IMAGE_NAME`:$VERSION"

Write-Host "Successfully published $FULL_IMAGE_NAME`:latest and $FULL_IMAGE_NAME`:$VERSION to Docker Hub" -ForegroundColor Green

# Update environment variable for docker-compose
Write-Host "Setting DOCKER_USERNAME environment variable for docker-compose" -ForegroundColor Cyan
$env:DOCKER_USERNAME = $DOCKER_USERNAME

Write-Host "Your docker-compose.yml is now configured to use $FULL_IMAGE_NAME`:latest" -ForegroundColor Green
Write-Host "You can now run: docker-compose up -d" -ForegroundColor Green
