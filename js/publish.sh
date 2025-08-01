#!/bin/bash
set -e

# Check if at least one package folder name is provided
if [ "$#" -le 0 ]; then
  echo "Error: Missing required argument package_name"
  echo "Usage: ./publish.sh <package_name>"
  exit 1
fi

MODULE="$1"
cd "$MODULE"

if [ -n "${TAG_NAME}" ]; then
    # Publish to npm public registry
    TAG_NAME=$(echo "${TAG_NAME}" | sed -E "s/^.*-v//")
    # Check if version contains 'b' (beta)
    if [[ "$TAG_NAME" == *"b"* ]]; then
        echo "Beta version detected: $TAG_NAME, publishing with beta tag"
        npm publish --access public --tag beta
    else
        echo "Release version detected: $TAG_NAME, publishing to latest"
        npm publish --access public
    fi
else
    echo "No release tag detected. Skipping binary upload."
fi
