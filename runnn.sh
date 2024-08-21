#!/bin/bash

# Define paths
SOURCE_FOLDER="/mnt/deadmanschest/shared/nmorabowen"
DESTINATION_FOLDER="/mnt/deadmanschest/nmorabowen"
SCRIPT_FILE="$DESTINATION_FOLDER/run.sh"

# Prompt for the new folder name
echo "Enter the name of the new folder:"
read NEW_FOLDER_NAME

# Define the new folder path
BASE_FOLDER="$SOURCE_FOLDER/$NEW_FOLDER_NAME"
NEW_FOLDER="$DESTINATION_FOLDER/$NEW_FOLDER_NAME"

# Step 1: Copy the entire folder from shared to the user's directory
cp -r "$BASE_FOLDER" "$NEW_FOLDER"

# Step 2: Copy the script file to the new folder
cp "$SCRIPT_FILE" "$NEW_FOLDER"

# Step 3: Replace 'nmbTEMP' with the new folder name in the run.sh file
sed -i "s/nmbTEMP/$NEW_FOLDER_NAME/g" "$NEW_FOLDER/run.sh"

# run command
cd "$NEW_FOLDER"
sbatch run.sh

echo "LARGA VIDA AL LADRUÑO!"
