#!/bin/bash

# Default values
DEFAULT_NODES=1
DEFAULT_TASKS_PER_NODE=16
JOB_NAME="nmbTEMP"
MODE="slurm"  # Default to SLURM mode

# Parse command-line arguments
# ./run.sh --nodes 1 --tasks-per-node 16 --job-name testJob --slurm
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --nodes) NODES="$2"; shift ;;  # Set the number of nodes
    --tasks-per-node) TASKS_PER_NODE="$2"; shift ;;  # Set tasks per node
    --job-name) JOB_NAME="$2"; shift ;;  # Set job name
    --local) MODE="local" ;;  # Switch to local mode
    *) echo "Unknown parameter passed: $1"; exit 1 ;;  # Handle invalid options
  esac
  shift
done

# Set defaults if not provided
NODES=${NODES:-$DEFAULT_NODES}
TASKS_PER_NODE=${TASKS_PER_NODE:-$DEFAULT_TASKS_PER_NODE}

if [[ "$MODE" == "slurm" ]]; then
  # SLURM mode
  #SBATCH --job-name="$JOB_NAME"
  #SBATCH --nodes="$NODES"
  #SBATCH --ntasks-per-node="$TASKS_PER_NODE"
  #SBATCH --output=log.log

  echo "Running with SLURM configuration:"
  echo "Job Name: $JOB_NAME"
  echo "Nodes: $NODES"
  echo "Tasks Per Node: $TASKS_PER_NODE"
else
  # Local mode
  echo "Running locally:"
  echo "Simulated Nodes: $NODES"
  echo "Simulated Tasks Per Node: $TASKS_PER_NODE"
fi

# Job setup
pwd; hostname; date
export OMP_NUM_THREADS=1
LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/mnt/nfshare/lib
SECONDS=0

if [[ "$MODE" == "slurm" ]]; then
  # SLURM execution
  mpirun /mnt/nfshare/bin/openseesmp-16102024
else
  # Local execution
  for ((node=1; node<=NODES; node++)); do
    echo "Simulating node $node with $TASKS_PER_NODE tasks..."
    for ((task=1; task<=TASKS_PER_NODE; task++)); do
      echo "Simulating task $task on node $node..."
    done
  done
  # Run OpenSees locally
  /mnt/nfshare/bin/openseesmp-16102024
fi

# Log completion
echo "Elapsed: $SECONDS seconds."
echo "Code finished successfully."
echo "LARGA VIDA AL LARUÑO!!!"
