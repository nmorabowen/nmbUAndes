# Usage:
# ./example_script.sh [--nodes NODES] [--tasks-per-node TASKS] [--dry-run]
#
# Parameters:
#   --nodes NODES            Specify the number of nodes to use. Default: 1.
#   --tasks-per-node TASKS   Specify the number of tasks per node. Default: 16.
#   --dry-run                Simulate all actions without making changes.
#
# Example Commands:
#   ./example_script.sh
#       Run the script with default settings (1 node, 16 tasks per node).
#
#   ./example_script.sh --nodes 2
#       Run the script with 2 nodes and default tasks per node (16).
#
#   ./example_script.sh --tasks-per-node 8
#       Run the script with default nodes (1) and 8 tasks per node.
#
#   ./example_script.sh --nodes 3 --tasks-per-node 32
#       Run the script with 3 nodes and 32 tasks per node.
#
#   DRY_RUN=true ./example_script.sh
#       Simulate all actions without copying files, updating scripts, or submitting jobs.
#
#   ./example_script.sh --nodes 4 --tasks-per-node 64 --dry-run
#       Simulate actions with 4 nodes and 64 tasks per node without executing them.

#!/bin/bash

# Configuration
LOG_FILE="script.log"
SOURCE_FOLDER="/mnt/deadmanschest/nmorabowen"
DESTINATION_FOLDER="/mnt/deadmanschest/nmorabowen"
SCRIPT_FILE="/mnt/deadmanschest/nmorabowen/nmbUAndes/run.sh"
DRY_RUN=false  # Set to true for testing without executing actions

# Default values for nodes and tasks
DEFAULT_NODES=1
DEFAULT_TASKS_PER_NODE=16
NODES=$DEFAULT_NODES
TASKS_PER_NODE=$DEFAULT_TASKS_PER_NODE

# Logging function
log() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $*" | tee -a "$LOG_FILE"
}

# Backup existing folder
backup_folder() {
  local folder="$1"
  local backup="$folder.bak_$(date +'%Y%m%d%H%M%S')"
  log "Backing up folder $folder to $backup..."
  if $DRY_RUN; then
    log "Dry run: Skipping actual backup."
  else
    mv "$folder" "$backup"
    log "Backup created at $backup."
  fi
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --nodes) NODES="$2"; shift ;;
    --tasks-per-node) TASKS_PER_NODE="$2"; shift ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

# Get the base folder name (last part of the path)
BASE_FOLDER_NAME=$(basename "$SOURCE_FOLDER")
NEW_FOLDER_NAME="${BASE_FOLDER_NAME}_run"

# Define paths
BASE_FOLDER="$SOURCE_FOLDER"
NEW_FOLDER="$DESTINATION_FOLDER/$NEW_FOLDER_NAME"

# Check if the folder already exists
while [ -d "$NEW_FOLDER" ]; do
  log "Folder $NEW_FOLDER_NAME already exists. What would you like to do?"
  echo "1) Remove the existing folder"
  echo "2) Backup the existing folder"
  echo "3) Stop the script"
  echo
  read -r OPTION
  echo

  case $OPTION in
    1)
      log "Removing existing folder $NEW_FOLDER..."
      if $DRY_RUN; then
        log "Dry run: Skipping actual removal."
      else
        rm -rf "$NEW_FOLDER"
        log "Existing folder removed."
      fi
      ;;
    2)
      backup_folder "$NEW_FOLDER"
      ;;
    3)
      log "Exiting script without making changes."
      exit 0
      ;;
    *)
      log "Invalid option. Please select 1, 2, or 3."
      ;;
  esac
done

# Step 1: Copy the folder
log "Copying $BASE_FOLDER to $NEW_FOLDER..."
if $DRY_RUN; then
  log "Dry run: Skipping actual copy."
else
  if cp -r "$BASE_FOLDER" "$NEW_FOLDER"; then
    log "Folder copied successfully."
  else
    log "Error: Failed to copy folder. Exiting script."
    exit 1
  fi
fi

# Step 2: Copy the script file
log "Copying script file to $NEW_FOLDER..."
if $DRY_RUN; then
  log "Dry run: Skipping actual script copy."
else
  if cp "$SCRIPT_FILE" "$NEW_FOLDER"; then
    log "Script file copied successfully."
  else
    log "Error: Failed to copy script file. Exiting script."
    exit 1
  fi
fi

# Step 3: Update job name, nodes, and tasks in run.sh
log "Updating job configuration in run.sh..."
if $DRY_RUN; then
  log "Dry run: Skipping actual update."
else
  sed -i "s/nmbTEMP/$NEW_FOLDER_NAME/g" "$NEW_FOLDER/run.sh" || { log "Error: Failed to update job name in run.sh."; exit 1; }
  sed -i "s/^#SBATCH --nodes=.*/#SBATCH --nodes=$NODES/" "$NEW_FOLDER/run.sh" || { log "Error: Failed to update nodes in run.sh."; exit 1; }
  sed -i "s/^#SBATCH --ntasks-per-node=.*/#SBATCH --ntasks-per-node=$TASKS_PER_NODE/" "$NEW_FOLDER/run.sh" || { log "Error: Failed to update tasks per node in run.sh."; exit 1; }
  log "Job configuration updated successfully in run.sh."
fi

# Run the job
log "Submitting job..."
if $DRY_RUN; then
  log "Dry run: Skipping job submission. Simulating local execution of run.sh."
  log "Simulated command: cd $NEW_FOLDER && ./run.sh --local --nodes $NODES --tasks-per-node $TASKS_PER_NODE"
else
  cd "$NEW_FOLDER" || { log "Error: Failed to change directory to $NEW_FOLDER. Exiting script."; exit 1; }
  if sbatch run.sh; then
    log "Job submitted successfully."
  else
    log "Error: Failed to submit job. Exiting script."
    exit 1
  fi
fi

log "------------------------------"
log "LARGA VIDA AL LADRUÑO!"
log "------------------------------"