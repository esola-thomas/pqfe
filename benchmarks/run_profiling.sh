# Copyright (c) 2025 Ernesto Sola-Thomas
#!/bin/bash

# Set variables
DOCKER_IMAGE="pqfe_profiling"
DOCKER_CONTAINER_NAME="pqfe_profiling_container"
RESULTS_DIR="./profiling_results"
LOG_FILE="$RESULTS_DIR/container_logs.txt"
STATS_FILE="$RESULTS_DIR/container_stats.txt"

# Default parameters
CPUS=1
MEMORY="20g"

# Process command-line arguments for Docker container
CONTAINER_ARGS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --cpus=*)
      CPUS="${1#*=}"
      shift
      ;;
    --memory=*)
      MEMORY="${1#*=}"
      shift
      ;;
    --min-size=*|--max-size=*|--steps=*|--scale=*|--graphs-only|--json-dir=*|--output-dir=*)
      CONTAINER_ARGS="$CONTAINER_ARGS $1"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--cpus=N] [--memory=SIZE] [--min-size=BYTES] [--max-size=BYTES] [--steps=N] [--scale=TYPE] [--graphs-only] [--json-dir=DIR] [--output-dir=DIR]"
      exit 1
      ;;
  esac
done

# Ensure the results directory exists
mkdir -p "$RESULTS_DIR"

# Build the Docker image
echo "Building Docker image..."
docker build -t "$DOCKER_IMAGE" . || exit 1

# Check if a container with the same name already exists
EXISTING_CONTAINER=$(docker ps -aq -f name="$DOCKER_CONTAINER_NAME")
if [ -n "$EXISTING_CONTAINER" ]; then
  echo "A container with the name $DOCKER_CONTAINER_NAME already exists. Removing it..."
  docker rm -f "$EXISTING_CONTAINER" || exit 1
fi

# Run the Docker container
echo "Running Docker container with parameters: $CONTAINER_ARGS"
docker run --name "$DOCKER_CONTAINER_NAME" \
  --cpus="$CPUS" \
  --memory="$MEMORY" \
  -v "$RESULTS_DIR:/ws/profiling_results" \
  "$DOCKER_IMAGE" > "$LOG_FILE" 2>&1 &

echo "Container started in background. View logs with: tail -f $LOG_FILE"

# Wait for a short period to ensure the container starts properly
sleep 15

# Get the container ID
CONTAINER_ID=$(docker ps -q -f name="$DOCKER_CONTAINER_NAME")

if [ -z "$CONTAINER_ID" ]; then
  echo "Failed to start the container. Check the logs at $LOG_FILE."
  exit 1
fi

echo "Container started with ID: $CONTAINER_ID"

# Monitor container stats and save to file
echo "Saving container stats to $STATS_FILE..."
docker stats "$CONTAINER_ID" --no-stream >> "$STATS_FILE"

# Wait for the container to finish
echo "Waiting for the container to complete..."
docker wait "$CONTAINER_ID"

# Save final stats
echo "Saving final container stats to $STATS_FILE..."
docker stats "$CONTAINER_ID" --no-stream >> "$STATS_FILE"

# Stop and remove the container
echo "Cleaning up..."
docker rm -f "$CONTAINER_ID"

echo "Profiling completed. Results saved in $RESULTS_DIR."
echo "Check logs at $LOG_FILE and container stats at $STATS_FILE."