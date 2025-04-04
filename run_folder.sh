#!/bin/bash

# === LOGGING ===
LOG_DIR="/mnt/deadmanschest/nmorabowen/logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/run_folder.log"
exec > >(tee -a "$LOG_FILE") 2>&1
echo "==== RECORDING AT $(date) ===="

# === USER INPUT ===
echo "Enter the job base name (used to generate unique job names):"
read -r BASE_JOB_NAME

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

    # === DETECT NUMBER OF PARTITIONS ===
    NUM_PARTS=$(find "$ST_FOLDER" -name "*.part-*.mpco.cdata" | wc -l)
    NUM_PARTS=${NUM_PARTS:-1}  # fallback to 1 if nothing found

    echo "  🧠 Found $NUM_PARTS partitions for ${ST_NAME}"

    # Remove existing run.sh if present
    [ -f "$TARGET_SCRIPT" ] && rm "$TARGET_SCRIPT"

    # Copy fresh template
    cp "$SCRIPT_SOURCE" "$TARGET_SCRIPT"

    # Replace job name placeholder
    sed -i "s/nmbTEMP/${BASE_JOB_NAME}_${RUP_NAME}_${ST_NAME}/g" "$TARGET_SCRIPT"

    echo "  → Configured run.sh for ${RUP_NAME}/${ST_NAME}"

    # Submit job using just --ntasks (SLURM will assign nodes)
    (
      cd "$ST_FOLDER" && \
      sbatch --ntasks="$NUM_PARTS" run.sh && \
      echo "  ✅ Submitted job with $NUM_PARTS tasks"
    ) || echo "  ❌ Failed to submit job in ${RUP_NAME}/${ST_NAME}"
  done
done

echo
echo "✅ All jobs submitted efficiently and scripts configured successfully."
echo "¡LARGA VIDA AL LADRUÑO!!! 🏴‍☠️"
