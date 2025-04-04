#!/bin/bash

# === CONFIGURATION ===
# Absolute path to the root folder containing the rup_bl_* folders
ROOT_DIR="/mnt/deadmanschest/nmorabowen/fixedBase"

# Path to the run.sh script to be copied
SCRIPT_SOURCE="/mnt/deadmanschest/nmorabowen/nmbUAndes/run.sh"

# === SCRIPT ===
# Loop over all rup_bl_* folders
for RUP_FOLDER in "$ROOT_DIR"/rup_bl_*; do
  RUP_NAME=$(basename "$RUP_FOLDER")

  echo "Processing rupture: $RUP_NAME"

  # Loop over all st* folders within the rupture folder
  for ST_FOLDER in "$RUP_FOLDER"/st*; do
    ST_NAME=$(basename "$ST_FOLDER")
    TARGET_SCRIPT="$ST_FOLDER/run.sh"

    # Copy run.sh to the station folder
    cp "$SCRIPT_SOURCE" "$TARGET_SCRIPT"

    # Replace 'nmbTEMP' with a unique job name like 'rup_bl_1_st0'
    sed -i "s/nmbTEMP/${RUP_NAME}_${ST_NAME}/g" "$TARGET_SCRIPT"

    echo "→ Copied and configured run.sh for ${RUP_NAME}/${ST_NAME}"
  done
done

echo
echo "✅ All run.sh scripts have been copied and customized."
