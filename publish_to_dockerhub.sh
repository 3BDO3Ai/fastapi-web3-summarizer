#!/bin/bash
set -e

# Configuration
IMAGE_NAME="web3-summarizer-api"
VERSION=$(date +"%Y%m%d%H%M")

# Check if username is provided
if [ -z "$1" ]; then
  echo "Error: Docker Hub username is required"
  echo "Usage: ./publish_to_dockerhub.sh YOUR_DOCKERHUB_USERNAME"
  exit 1
fi

DOCKER_USERNAME=$1
FULL_IMAGE_NAME="$DOCKER_USERNAME/$IMAGE_NAME"

echo "Building Docker image: $FULL_IMAGE_NAME:latest and $FULL_IMAGE_NAME:$VERSION"

# Build the Docker image
docker build -t "$FULL_IMAGE_NAME:latest" -t "$FULL_IMAGE_NAME:$VERSION" .

# Log in to Docker Hub (will prompt for password if not already logged in)
echo "Logging in to Docker Hub as $DOCKER_USERNAME"
docker login -u "$DOCKER_USERNAME"

# Push the images to Docker Hub
echo "Pushing images to Docker Hub"
docker push "$FULL_IMAGE_NAME:latest"
docker push "$FULL_IMAGE_NAME:$VERSION"

echo "Successfully published $FULL_IMAGE_NAME:latest and $FULL_IMAGE_NAME:$VERSION to Docker Hub"

# Update docker-compose.yml with the correct username
echo "Updating docker-compose.yml with your username"
export DOCKER_USERNAME=$DOCKER_USERNAME
echo "Your docker-compose.yml is now configured to use $FULL_IMAGE_NAME:latest"
echo "You can now run: docker-compose up -d"
