#!/bin/bash
set -euo pipefail

# === ARGS ===
OVERRIDE_PARTS=""
DRY_RUN=0
VERBOSE=0
while getopts "p:nv" opt; do
  case $opt in
    p) OVERRIDE_PARTS="$OPTARG" ;;
    n) DRY_RUN=1 ;;
    v) VERBOSE=1 ;;
    *) echo "Usage: $0 [-p num_partitions] [-n] [-v] [ROOT_DIR]" >&2; exit 1 ;;
  esac
done
shift $((OPTIND - 1))

# === LOGGING ===
LOG_DIR="/mnt/deadmanschest/nmorabowen/logs"
mkdir -p "$LOG_DIR"
STAMP="$(date +'%Y%m%d_%H%M%S')"
LOG_FILE="$LOG_DIR/run_recursive_$STAMP.log"
exec > >(tee -a "$LOG_FILE") 2>&1
echo "==== RECURSIVE MOVE RUN at $(date) ===="

# === ROOT ===
if [[ -n "${1:-}" ]]; then
  ROOT_DIR="$1"
else
  read -r -p "Enter the root folder to search for analyses (e.g. /mnt/deadmanschest/nmorabowen/): " ROOT_DIR
fi
if [[ ! -d "$ROOT_DIR" ]]; then
  echo "❌ Folder '$ROOT_DIR' does not exist."
  exit 1
fi

# === CONFIG ===
SCRIPT_TEMPLATE="/mnt/deadmanschest/nmorabowen/nmbUAndes/run_move.sh"

# === FIND FOLDERS ===
echo "🔍 Searching for analysis folders under: $ROOT_DIR"
mapfile -t ANALYSIS_FOLDERS < <(find "$ROOT_DIR" -type f -name "main.tcl" -printf '%h\n' | sort -u)

if (( ${#ANALYSIS_FOLDERS[@]} == 0 )); then
  echo "⚠️  No folders with main.tcl found under $ROOT_DIR."
  exit 0
fi

# === LOOP ===
for ST_FOLDER in "${ANALYSIS_FOLDERS[@]}"; do
  ST_NAME="$(basename "$ST_FOLDER")"
  PARENT_NAME="$(basename "$(dirname "$ST_FOLDER")")"
  JOB_NAME="${PARENT_NAME}_${ST_NAME}"
  TARGET_SCRIPT="$ST_FOLDER/run_move.sh"

  # DETECT PARTS
  mapfile -t PART_NUMBERS < <(find "$ST_FOLDER" -type f -name "*.part-*.mpco.cdata" \
    | sed -E 's/.*\.part-([0-9]+)\.mpco\.cdata/\1/' | sort -n | uniq)

  if (( ${#PART_NUMBERS[@]} == 0 )); then
    NUM_PARTS=1; MAX_PART=0
  else
    NUM_PARTS=${#PART_NUMBERS[@]}
    MAX_PART="${PART_NUMBERS[-1]}"
  fi

  ACTUAL_PARTS=$((MAX_PART + 1))
  if (( NUM_PARTS != ACTUAL_PARTS )); then
    echo "⚠️  Inconsistent partitions in: $ST_FOLDER"
    echo "    Unique count: $NUM_PARTS  Max index: $MAX_PART  (implying $ACTUAL_PARTS)"
    # pick the safer higher value
    if (( ACTUAL_PARTS > NUM_PARTS )); then
      NUM_PARTS=$ACTUAL_PARTS
    fi
  fi

  if [[ -n "$OVERRIDE_PARTS" && "$OVERRIDE_PARTS" -gt 0 ]]; then
    echo "📁 $ST_FOLDER → Using override: $OVERRIDE_PARTS partitions (auto: $NUM_PARTS)"
    NUM_PARTS="$OVERRIDE_PARTS"
  else
    echo "📁 $ST_FOLDER → $NUM_PARTS partitions"
  fi

  # CREATE run_move.sh IF MISSING
  if [[ ! -f "$TARGET_SCRIPT" ]]; then
    cp -f "$SCRIPT_TEMPLATE" "$TARGET_SCRIPT"
    # Only replace placeholder if present
    if grep -q 'nmbTEMP' "$TARGET_SCRIPT"; then
      sed -i.bak "s/nmbTEMP/${JOB_NAME}/g" "$TARGET_SCRIPT"
    fi
    chmod +x "$TARGET_SCRIPT"
    (( VERBOSE )) && echo "  ↳ Created $TARGET_SCRIPT"
  fi

  # SUBMIT
  if (( DRY_RUN )); then
    echo "  ⚙️  DRY-RUN: sbatch --ntasks=\"$NUM_PARTS\" --chdir=\"$ST_FOLDER\" run_move.sh"
  else
    if sbatch --ntasks="$NUM_PARTS" --chdir="$ST_FOLDER" run_move.sh; then
      echo "  ✅ Submitted MOVE job: $JOB_NAME ($NUM_PARTS tasks)"
    else
      echo "  ❌ Failed to submit job in $ST_FOLDER"
    fi
  fi
done

echo
echo "✅ All run_move jobs submitted."
echo "LARGA VIDA AL LADRUÑO!!! 🏴‍☠️"
