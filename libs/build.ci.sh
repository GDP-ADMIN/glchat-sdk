#!/bin/bash
set -e

# shellcheck source=/dev/null
source ./shared.sh

# Check if at least one package folder name is provided
if [ "$#" -le 1 ]; then
  echo "Error: Missing required argument package_name"
  echo "Usage: ./build.ci.sh <package_name> <package_version>"
  echo "- package_version must follow semantic version PEP440, default (0.0.0)."
  echo "  https://peps.python.org/pep-0440/"
  echo "- Available package_name options:"
  echo "---"
  echo "$(echo "$(ls)" | grep gllm-)"
  echo "---"
  exit 1
fi

MODULE="$1"
VERSION="$2"

PEP440_REGEX='^([0-9]+!)?([0-9]+(\.[0-9]+)*)((a|b|rc)[0-9]+)?(\.post[0-9]+)?(\.dev[0-9]+)?(\+([a-zA-Z0-9]+(\.[a-zA-Z0-9]+)*))?$'

# Perform the regex match
if [[ "$VERSION" =~ $PEP440_REGEX ]]; then
    echo "Valid version: $VERSION"
else
    echo "Invalid version: $VERSION. Overriding to 0.0.0."
    VERSION="0.0.0"
fi

echo "Using version: $VERSION"

cd "$MODULE" || { echo "Module/Package directory not found"; exit 1; }

install_system_dependencies
configure_poetry_auth
configure_build_files "$VERSION"
modify_pyproject_toml "$MODULE"
install_dependencies

MODULE_DIR=$(convert_to_snake_case "$MODULE")

# Run quality checks and tests
run_pre_commit "./"
run_tests

# Build the package
build_with_nuitka "$MODULE_DIR"

cd ..
