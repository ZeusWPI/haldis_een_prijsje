#!/bin/bash

# Define variables
IMAGE_NAME="haldis-een-prijsje"
VOLUME_NAME="$(pwd)/hlds_files"
DOCKERFILE_DIR="."
DOCKERFILE_NAME="Dockerfile.scraper"
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
    echo "Building Docker image: $IMAGE_NAME ..."
    docker build -f "$DOCKERFILE_NAME" -t $IMAGE_NAME $DOCKERFILE_DIR
    if [ $? -ne 0 ]; then
        echo "Docker build failed. Exiting."
        exit 1
    fi
    echo "Docker image built successfully."
else
    echo "Skipping Docker image rebuild (--no-rebuild flag provided)."
fi

# Ensure the output directory exists
if [ ! -d "$VOLUME_NAME" ]; then
    echo "Creating output directory: $VOLUME_NAME ..."
    mkdir -p "$VOLUME_NAME"
fi

# Run the Docker container with arguments
echo "Running Docker container..."
docker run -v "$VOLUME_NAME:/haldis/hlds_files" $IMAGE_NAME "$@"
EXIT_CODE=$?

# Print result
if [ $EXIT_CODE -eq 0 ]; then
    echo "Docker container executed successfully."
else
    echo "Docker container failed with exit code $EXIT_CODE."
fi
