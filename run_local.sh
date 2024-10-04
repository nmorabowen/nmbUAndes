#!/bin/bash

# Define paths
SOURCE_FOLDER="/mnt/deadmanschest/nmorabowen"
DESTINATION_FOLDER="/mnt/deadmanschest/nmorabowen"
SCRIPT_FILE="/mnt/deadmanschest/nmorabowen/nmbUAndes/run.sh"

# Prompt for the new folder name
echo "Enter the name of the new folder:"
read NEW_FOLDER_NAME

# Define the new folder path
BASE_FOLDER="$SOURCE_FOLDER/$NEW_FOLDER_NAME"
NEW_FOLDER="$DESTINATION_FOLDER/$NEW_FOLDER_NAME"

# Check if the folder already exists
while [ -d "$NEW_FOLDER" ]; do
  echo "Folder $NEW_FOLDER_NAME already exists. What would you like to do?"
  echo "1) Remove the existing folder"
  echo "2) Enter a new name"
  echo "3) Stop the script"
  echo

  read -r OPTION
  echo

  case $OPTION in
    1)
      rm -rf "$NEW_FOLDER"
      echo "Existing folder removed."
      ;;
    2)
      NEW_FOLDER_NAME="${NEW_FOLDER_NAME}_res"
      NEW_FOLDER="$DESTINATION_FOLDER/$NEW_FOLDER_NAME"
      ;;
    3)
      echo "Exiting script without making changes."
      exit 0
      ;;
    *)
      echo "Invalid option. Please select 1, 2, or 3."
      ;;
  esac
done

echo

# Step 1: Copy the entire folder from shared to the user's directory
if cp -r "$BASE_FOLDER" "$NEW_FOLDER"; then
  echo "Folder copied successfully."
else
  echo "Failed to copy folder. Exiting script."
  echo
  exit 1
fi

# Step 2: Copy the script file to the new folder
if cp "$SCRIPT_FILE" "$NEW_FOLDER"; then
  echo "Script file copied successfully."
else
  echo "Failed to copy script file. Exiting script."
  echo
  exit 1
fi

# Step 3: Replace 'nmbTEMP' with the new folder name in the run.sh file
if sed -i "s/nmbTEMP/$NEW_FOLDER_NAME/g" "$NEW_FOLDER/run.sh"; then
  echo "Job name updated successfully in run.sh."
  echo
else
  echo "Failed to update job name in run.sh. Exiting script."
  echo
  exit 1
fi

# Run command
cd "$NEW_FOLDER" || { echo "Failed to change directory to $NEW_FOLDER. Exiting script."; exit 1; }
if sbatch run.sh; then
  echo "Job submitted successfully."
  echo
else
  echo "Failed to submit job. Exiting script."
  echo
  exit 1
fi

echo 
echo "------------------------------"
echo "LARGA VIDA AL LADRUÑO!"
echo "------------------------------"
