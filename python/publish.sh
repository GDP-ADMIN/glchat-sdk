#!/bin/bash
set -e

# Check if at least one package folder name is provided
if [ "$#" -le 0 ]; then
  echo "Error: Missing required argument package_name"
  echo "Usage: ./build.ci.sh <package_name> <package_version>"
  echo "- package_version must follow semantic version PEP440, default (0.0.0)."
  echo "  https://peps.python.org/pep-0440/"
  exit 1
fi

MODULE="$1"
cd "$MODULE"

if [ -n "${TAG_NAME}" ]; then
    # Publish to PyPI
    uv publish --no-cache
else
    echo "No release tag detected. Skipping binary upload."
fi
