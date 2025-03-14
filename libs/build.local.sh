#!/bin/bash
set -xe

# Check if at least one package folder name is provided
if [ "$#" -lt 1 ]; then
  echo "Error: No package folder names provided."
  echo "Usage: ./build.local.sh <gllm-docproc> <gllm-retrieval> ... <package_name_n>"
  exit 1
fi

# shellcheck source=/dev/null
source ../.ci/shared.sh

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

  echo "Building package: $PACKAGE_NAME"

  # Build the package using poetry and nuitka
  poetry run nuitka --module "$PACKAGE_NAME" --include-package="$PACKAGE_NAME"

  # Delete *.build directories to prevent errors when building the wheel
  find . -type d -name "*.build" -exec rm -rf {} +

  # Generate pyi files
  poetry run stubgen --include-docstrings -p "$PACKAGE_NAME"

  # Copy the result into the package
  cp -a out/"$PACKAGE_NAME" .

  # Delete the pyi output directory
  rm -rf out

  # update include & exclude rules in pyproject.toml
  add_rules

  echo "Building wheel for $PACKAGE_NAME"
  # Build the wheel
  poetry build --format wheel

  echo "Completed building: $PACKAGE_NAME"

  # Remove include & exclude rules from pyproject.toml
  remove_rules

  # Move back to the parent directory (libs)
  popd
done

# Final cleanup tasks after all packages are built
echo "Cleaning up..."

# Cleanup .pyi and .so files
find . -name "*.pyi" -delete
find . -name "*.so" -delete
find . -name "pyproject.toml''" -delete

echo "Cleaning up completed"
