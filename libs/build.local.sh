#!/bin/bash
set -e

# Check if at least one package folder name is provided
if [ "$#" -lt 1 ]; then
  echo "Error: No package folder names provided."
  echo "Usage: ./build.local.sh <gllm-docproc> <gllm-retrieval> ... <package_name_n>"
  exit 1
fi

echo "Build started..."

# Loop through each package folder name provided as arguments
for FOLDER_NAME in "$@"
do
  # Convert folder name (with hyphens) to package name (with underscores)
  PACKAGE_NAME=$(echo "$FOLDER_NAME" | tr '-' '_')

  # Enter the package directory
  if [ -d "$FOLDER_NAME" ]; then
    pushd "$FOLDER_NAME" || exit
  else
    echo "Error: Folder $FOLDER_NAME does not exist."
    exit 1
  fi

  echo "Install dependencies..."
  # install nutika & mypy in the virtual environment
  poetry install --with compiler

  echo "Building wheel for $PACKAGE_NAME"
  # Build the wheel
  poetry run stubgen --include-docstrings -p "${PACKAGE_NAME}" -o .
  poetry build --format wheel

  echo "Completed building: $PACKAGE_NAME"

  # Move back to the parent directory (libs)
  popd
done
