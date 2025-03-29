# Copyright (c) 2025 Ernesto Sola-Thomas
#!/bin/bash

# Wrapper script to control the number of CPU cores assigned to the Python script

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <num_cores> <python_script> [script_args...]"
  exit 1
fi

NUM_CORES=$1
PYTHON_SCRIPT=$2
shift 2

# Set CPU affinity for the current shell and its child processes
if command -v taskset &> /dev/null; then
  echo "Running with $NUM_CORES cores using taskset..."
  taskset -c 0-$(($NUM_CORES - 1)) python "$PYTHON_SCRIPT" "$@"
else
  echo "Error: taskset command not found. Please install it to use this script."
  exit 1
fi