#!/bin/bash

# === LOGGING ===
LOG_DIR="/mnt/deadmanschest/nmorabowen/logs"
mkdir -p "$LOG_DIR"  # Create it if it doesn't exist

LOG_FILE="$LOG_DIR/run_folder.log"
exec > >(tee -a "$LOG_FILE") 2>&1
echo "==== RECORDING AT $(date) ===="

# === USER INPUT ===
echo "Enter the job base name (used to generate unique job names):"
read -r BASE_JOB_NAME

echo "Enter the number of nodes [default: 1]:"
read -r NODES
NODES=${NODES:-1}

echo "Enter the number of tasks per node [default: 8]:"
read -r TASKS_PER_NODE
TASKS_PER_NODE=${TASKS_PER_NODE:-8}

# === CONFIGURATION ===
SEARCH_DIR="/mnt/deadmanschest/nmorabowen"
ROOT_DIR="$SEARCH_DIR/$BASE_JOB_NAME"
SCRIPT_SOURCE="/mnt/deadmanschest/nmorabowen/nmbUAndes/run.sh"

# === CHECK ROOT FOLDER EXISTS ===
if [ ! -d "$ROOT_DIR" ]; then
  echo
  echo "❌ The folder '$ROOT_DIR' does not exist."
  echo "Please check the base job name and try again."
  echo
  exit 1
fi

# === MAIN LOOP ===
for RUP_FOLDER in "$ROOT_DIR"/rup_bl_*; do
  RUP_NAME=$(basename "$RUP_FOLDER")
  echo "🔁 Processing rupture: $RUP_NAME"

  for ST_FOLDER in "$RUP_FOLDER"/st*; do
    ST_NAME=$(basename "$ST_FOLDER")
    TARGET_SCRIPT="$ST_FOLDER/run.sh"

    # Remove existing run.sh if present
    [ -f "$TARGET_SCRIPT" ] && rm "$TARGET_SCRIPT"

    # Copy fresh template
    cp "$SCRIPT_SOURCE" "$TARGET_SCRIPT"

    # Replace job name placeholder
    sed -i "s/nmbTEMP/${BASE_JOB_NAME}_${RUP_NAME}_${ST_NAME}/g" "$TARGET_SCRIPT"

    echo "  → Configured run.sh for ${RUP_NAME}/${ST_NAME}"

    # Submit job with user-defined resources
    (
      cd "$ST_FOLDER" && \
      sbatch --nodes="$NODES" --ntasks-per-node="$TASKS_PER_NODE" run.sh && \
      echo "  ✅ Submitted job for ${RUP_NAME}/${ST_NAME}"
    ) || echo "  ❌ Failed to submit job in ${RUP_NAME}/${ST_NAME}"
  done
done

echo
echo "✅ All jobs submitted and scripts configured successfully."
echo "¡LARGA VIDA AL LADRUÑO!!! 🏴‍☠️"
