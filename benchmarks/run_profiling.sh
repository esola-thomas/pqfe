#!/bin/bash

# filepath: /home/esola-thomas/Electrical_and_Computer_Master_Thesis/run_profiling.sh

# Set variables
DOCKER_IMAGE="pqfe_profiling"
DOCKER_CONTAINER_NAME="pqfe_profiling_container"
RESULTS_DIR="/home/esola-thomas/Electrical_and_Computer_Master_Thesis/profiling_results"
LOG_FILE="$RESULTS_DIR/container_logs.txt"
STATS_FILE="$RESULTS_DIR/container_stats.txt"

# Ensure the results directory exists
mkdir -p "$RESULTS_DIR"

# Build the Docker image
echo "Building Docker image..."
docker build -t "$DOCKER_IMAGE" /home/esola-thomas/Electrical_and_Computer_Master_Thesis/external/pqfe || exit 1

# Run the Docker container in detached mode
echo "Running Docker container..."
# docker run -d --name "$DOCKER_CONTAINER_NAME" --cpus=1 --memory=8g \
#   -v "$RESULTS_DIR:/ws/profiling_results" "$DOCKER_IMAGE" > "$LOG_FILE" 2>&1
docker run --cpus=1 --memory=16g -v /home/esola-thomas/Electrical_and_Computer_Master_Thesis/profiling_results:/ws/profiling_results pqfe_profiling > /home/esola-thomas/Electrical_and_Computer_Master_Thesis/profiling_results/container_logs.txt 2>&1
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

echo "Profiling completed. Logs and stats saved in $RESULTS_DIR."