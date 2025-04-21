#!/bin/bash
# shellcheck disable=SC2064
set -e

# shellcheck source=/dev/null
source ./shared.sh

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
  trap "git checkout -- '$FOLDER_NAME/$(convert_to_snake_case "$FOLDER_NAME")' '$FOLDER_NAME/poetry.lock' '$FOLDER_NAME/pyproject.toml'" EXIT
  echo "Processing package: $FOLDER_NAME"
  if [ -d "$FOLDER_NAME" ]; then
    cd "$FOLDER_NAME" || exit
  else
    echo "Error: Folder $FOLDER_NAME does not exist."
    exit 1
  fi

  install_system_dependencies
  gcloud auth print-access-token > token.key
  configure_poetry_auth token.key
  configure_build_files "$FOLDER_NAME"
  modify_pyproject_toml "$FOLDER_NAME"
  install_dependencies

  PACKAGE_NAME=$(convert_to_snake_case "$FOLDER_NAME")

  echo "Running quality checks..."
  run_pre_commit "./"
  
  echo "Running tests..."
  run_tests

  echo "Building package: $PACKAGE_NAME"
  build_with_nuitka "$PACKAGE_NAME"

  echo "✅ Completed building: $PACKAGE_NAME"

  # Move back to the parent directory (libs)
  cd ..
done

echo "✅ All packages built successfully!"
