#!/bin/bash

# === PARSE COMMAND LINE ARGS ===
OVERRIDE_PARTS=""
while getopts "p:" opt; do
  case $opt in
    p) OVERRIDE_PARTS="$OPTARG" ;;
    *) echo "Usage: $0 [-p num_partitions]" >&2; exit 1 ;;
  esac
done

# === LOGGING ===
LOG_DIR="/mnt/deadmanschest/nmorabowen/logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/run_recursive.log"
exec > >(tee -a "$LOG_FILE") 2>&1
echo "==== RECURSIVE RUN at $(date) ===="

# === USER INPUT ===
echo "Enter the root folder to search for analyses (e.g. /mnt/deadmanschest/nmorabowen/fixedBase):"
read -r ROOT_DIR

# === SCRIPT CONFIG ===
SCRIPT_SOURCE="/mnt/deadmanschest/nmorabowen/nmbUAndes/run.sh"

# === VALIDATE ROOT ===
if [ ! -d "$ROOT_DIR" ]; then
  echo "❌ Folder '$ROOT_DIR' does not exist."
  exit 1
fi

# === FIND ALL FOLDERS CONTAINING main.tcl ===
echo "🔍 Searching for analysis folders under: $ROOT_DIR"
ANALYSIS_FOLDERS=$(find "$ROOT_DIR" -type f -name "main.tcl" -exec dirname {} \;)

if [ -z "$ANALYSIS_FOLDERS" ]; then
  echo "⚠️ No folders with main.tcl found under $ROOT_DIR."
  exit 0
fi

# === LOOP OVER ANALYSIS FOLDERS ===
for ST_FOLDER in $ANALYSIS_FOLDERS; do
  ST_NAME=$(basename "$ST_FOLDER")
  PARENT_NAME=$(basename "$(dirname "$ST_FOLDER")")
  JOB_NAME="${PARENT_NAME}_${ST_NAME}"
  TARGET_SCRIPT="$ST_FOLDER/run.sh"

  # DETECT PARTITIONS - Get unique partition numbers from filenames
  PART_NUMBERS=$(find "$ST_FOLDER" -name "*.part-*.mpco.cdata" | sed -E 's/.*\.part-([0-9]+)\.mpco\.cdata/\1/' | sort -n | uniq)
  NUM_PARTS=$(echo "$PART_NUMBERS" | wc -l)
  MAX_PART=$(echo "$PART_NUMBERS" | tail -1)
  
  # If no parts found, default to 1
  if [ -z "$PART_NUMBERS" ]; then
    NUM_PARTS=1
    MAX_PART=0
  fi
  
  # Calculate actual number of partitions (max part number + 1, since we start from 0)
  ACTUAL_PARTS=$((MAX_PART + 1))
  
  # Sanity check - if something went wrong with detection
  if [ "$NUM_PARTS" != "$ACTUAL_PARTS" ]; then
    echo "⚠️ Warning: Inconsistent partition numbers detected in $ST_FOLDER"
    echo "   Found $NUM_PARTS unique partition numbers but max partition is $MAX_PART"
    # Use the higher number to be safe
    NUM_PARTS=$((NUM_PARTS > ACTUAL_PARTS ? NUM_PARTS : ACTUAL_PARTS))
  fi
  
  # USE OVERRIDE IF PROVIDED
  if [ -n "$OVERRIDE_PARTS" ] && [ "$OVERRIDE_PARTS" -gt 0 ]; then
    echo "📁 Found analysis in $ST_FOLDER → Using $OVERRIDE_PARTS partitions (auto-detected: $NUM_PARTS)"
    NUM_PARTS=$OVERRIDE_PARTS
  else
    echo "📁 Found analysis in $ST_FOLDER → $NUM_PARTS partitions"
  fi

  # PREPARE run.sh
  [ -f "$TARGET_SCRIPT" ] && rm "$TARGET_SCRIPT"
  cp "$SCRIPT_SOURCE" "$TARGET_SCRIPT"
  sed -i "s/nmbTEMP/${JOB_NAME}/g" "$TARGET_SCRIPT"

  # SUBMIT JOB
  (
    cd "$ST_FOLDER" && \
    sbatch --ntasks="$NUM_PARTS" run.sh && \
    echo "  ✅ Submitted job: $JOB_NAME ($NUM_PARTS tasks)"
  ) || echo "  ❌ Failed to submit job in $ST_FOLDER"
done

echo
echo "✅ All recursive jobs submitted successfully."
echo "LARGA VIDA AL LADRUÑO!!! 🏴‍☠️"