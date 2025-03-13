#!/bin/bash
# shellcheck disable=SC2035
# References:
#     - https://github.com/GDP-ADMIN/gen-ai-internal/blob/main/libs/shared.sh

PYPROJECT_TOML="pyproject.toml"
# Get the absolute path to the .ci directory
CI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Global regex pattern for finding internal dependencies
INTERNAL_DEPS_REGEX='(gllm|bosa)[-_][a-zA-Z0-9_-]+'

# Detect if the system is macOS or Linux for sed compatibility
if [[ "$OSTYPE" == "darwin"* ]]; then
    SED_INPLACE="sed -i ''"
else
    SED_INPLACE="sed -i"
fi

function binary_build {
  # shellcheck disable=SC2001,SC2153
  PACKAGE_NAME=$(echo "$MODULE" | sed 's/-/_/g')
  echo "Building package: $PACKAGE_NAME"
  poetry run nuitka --verbose --mode=package "$PACKAGE_NAME"
  find . -type d -name "*.build" -exec rm -rf {} +

  echo "Generating python interface files..."
  poetry run stubgen --include-docstrings -p "$PACKAGE_NAME"
  cp -a out/"$PACKAGE_NAME" .
  rm -rf out

  echo "Building wheel for $PACKAGE_NAME"
  poetry build --format wheel
  python "$CI_DIR/update_whl.py" "$PACKAGE_NAME"

  echo "Cleaning up..."
  find "$PACKAGE_NAME" -name "*.pyi" -delete
  rm "$PACKAGE_NAME"'.pyi'
  find "$PACKAGE_NAME" -name "*.so" -delete
  find . -name "pyproject.toml" -delete
  rm -f -- *.so

  echo "Cleaning up completed"
}
