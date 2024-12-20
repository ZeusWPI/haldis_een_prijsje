#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define the Docker image name, container name, and Dockerfile name
IMAGE_NAME="haldis_website"
CONTAINER_NAME="haldis_website_container"
DOCKERFILE_NAME="Dockerfile"  # Variable for Dockerfile name
VOLUME_NAME="$(pwd)/hlds_files"

NO_REBUILD=false

# Parse arguments
for arg in "$@"; do
    if [ "$arg" == "--no-rebuild" ]; then
        NO_REBUILD=true
        shift # Remove the flag from arguments
        break
    fi
done

# Build the Docker image (unless --no-rebuild is specified)
if [ "$NO_REBUILD" == false ]; then
    # Step 1: Build the Docker image using the specified Dockerfile
    echo "Building the Docker image using $DOCKERFILE_NAME..."
    docker build -f $DOCKERFILE_NAME -t $IMAGE_NAME .
    if [ $? -ne 0 ]; then
        echo "Docker build failed. Exiting."
        exit 1
    fi
    echo "Docker image built successfully."
else
    echo "Skipping Docker image rebuild (--no-rebuild flag provided)."
fi

# Step 2: Check if a container with the same name is already running
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping existing container..."
    docker stop $CONTAINER_NAME
    echo "Removing existing container..."
    docker rm $CONTAINER_NAME
fi

# Step 3: Run the Docker container
echo "Running the Docker container..."
docker run -d -p 5000:5000 -v "$VOLUME_NAME:/haldis_prijsje/hlds_files" --name $CONTAINER_NAME $IMAGE_NAME

# Step 4: Output the URL where the website can be accessed
echo "Website is now running at: http://127.0.0.1:5000"
