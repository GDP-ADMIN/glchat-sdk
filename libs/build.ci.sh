#!/bin/bash
set -e

# shellcheck source=/dev/null
source ./shared.sh

# Check if at least one package folder name is provided
if [ "$#" -ne 1 ]; then
  echo "Error: No package folder name provided."
  echo "Usage: ./build.ci.sh <package_name>"
  exit 1
fi

cd "$MODULE"

install_system_dependencies
configure_poetry_auth
configure_build_files "$MODULE"
modify_pyproject_toml "$MODULE"
install_dependencies

MODULE_DIR=$(convert_to_snake_case "$MODULE")

# Run quality checks and tests
run_pre_commit "./"
run_tests

# Build the package
build_with_nuitka "$MODULE_DIR"

cd ..
