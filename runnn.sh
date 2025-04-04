#!/bin/bash

# === LOGGING ===
LOG_DIR="/mnt/deadmanschest/nmorabowen/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/run_one.log"
exec > >(tee -a "$LOG_FILE") 2>&1
echo "==== SINGLE ANALYSIS at $(date) ===="

# === USER INPUT ===
echo "Enter the full path to the analysis folder:"
read -r ANALYSIS_FOLDER

# Check if folder exists
if [ ! -d "$ANALYSIS_FOLDER" ]; then
  echo "❌ Folder '$ANALYSIS_FOLDER' does not exist."
  exit 1
fi

# === SETTINGS ===
SCRIPT_SOURCE="/mnt/deadmanschest/nmorabowen/nmbUAndes/run.sh"
TARGET_SCRIPT="$ANALYSIS_FOLDER/run.sh"

# === DETECT PARTITIONS ===
NUM_PARTS=$(find "$ANALYSIS_FOLDER" -name "*.part-*.mpco.cdata" | wc -l)
NUM_PARTS=${NUM_PARTS:-8}  # fallback a 8 si no hay archivos encontrados

# === GENERATE JOB NAME ===
FOLDER_NAME=$(basename "$ANALYSIS_FOLDER")
JOB_NAME="single_${FOLDER_NAME}"

# === PREPARE run.sh ===
[ -f "$TARGET_SCRIPT" ] && rm "$TARGET_SCRIPT"
cp "$SCRIPT_SOURCE" "$TARGET_SCRIPT"
sed -i "s/nmbTEMP/${JOB_NAME}/g" "$TARGET_SCRIPT"

# === SUBMIT ===
echo "📦 Submitting '$FOLDER_NAME' with $NUM_PARTS task(s)..."
(
  cd "$ANALYSIS_FOLDER" && \
  sbatch --ntasks="$NUM_PARTS" run.sh && \
  echo "✅ Job submitted successfully."
) || echo "❌ Failed to submit job."

echo
echo "LARGA VIDA AL LADRUÑO! 🏴‍☠️"
