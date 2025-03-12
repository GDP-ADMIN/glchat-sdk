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

set +x

function binary_build {
  # shellcheck disable=SC2001,SC2153
  PACKAGE_NAME=$(echo "$MODULE" | sed 's/-/_/g')
  echo "Install dependencies..."

  echo "Building package: $PACKAGE_NAME"

  # Extract internal dependencies from pyproject.toml
  INCLUDE_PACKAGES="$PACKAGE_NAME"
  if [ -f "$PYPROJECT_TOML" ]; then
    echo "Scanning $PYPROJECT_TOML for internal dependencies..."
    DIRECT_DEPS=$(awk '/^\[tool\.poetry\.dependencies\]/{flag=1;next}/^\[/{flag=0}flag' "$PYPROJECT_TOML" | grep -E "^($INTERNAL_DEPS_REGEX)" | awk -F '[ ={}]' '{print $1}' | sed 's/-/_/g' | sort -u)
    TABLE_DEPS=$(grep -E "^\[tool\.poetry\.dependencies\.($INTERNAL_DEPS_REGEX)\]" "$PYPROJECT_TOML" | grep -oE "\.($INTERNAL_DEPS_REGEX)\]" | grep -oE "($INTERNAL_DEPS_REGEX)" | sed 's/-/_/g' | sort -u)
    DEPS="$DIRECT_DEPS $TABLE_DEPS"
    
    echo "Found direct dependencies: $DIRECT_DEPS"
    echo "Found table dependencies: $TABLE_DEPS"
    echo "Combined dependencies: $DEPS"
    
    if [ -n "$DEPS" ]; then
      for DEP in $DEPS; do
        if [ "$DEP" != "$PACKAGE_NAME" ]; then
          INCLUDE_PACKAGES="$INCLUDE_PACKAGES,$DEP"
          echo "Adding dependency to include: $DEP"
        fi
      done
    fi
  else
    echo "Warning: $PYPROJECT_TOML not found, using only $PACKAGE_NAME"
  fi
  
  echo "Including packages: $INCLUDE_PACKAGES"
  poetry run nuitka --verbose --module "$PACKAGE_NAME" --include-package="$INCLUDE_PACKAGES"

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

  # Update whl
  python "$CI_DIR/update_whl.py" "$PACKAGE_NAME"

  echo "Completed building: $PACKAGE_NAME"

  # Remove include & exclude rules from pyproject.toml
  remove_rules
  # Final cleanup tasks after all packages are built
  echo "Cleaning up..."

  # Cleanup .pyi and .so files
  find "$PACKAGE_NAME" -name "*.pyi" -delete
  rm "$PACKAGE_NAME"'.pyi'
  find "$PACKAGE_NAME" -name "*.so" -delete
  find . -name "pyproject.toml''" -delete
  rm -f -- *.so

  echo "Cleaning up completed"
}

function update_pyproject {
   cp pyproject.toml pyproject.toml.backup
   pip install toml
   python "$CI_DIR/update_pyproject.py"
}

# Function to add include and exclude rules
add_rules() {
    echo "Adding include and exclude rules..."

    # Step 1: Add or update the exclude rule under [tool.poetry]
    if grep -q '\[tool.poetry\]' $PYPROJECT_TOML && grep -A 5 '\[tool.poetry\]' $PYPROJECT_TOML | grep -q 'exclude'; then
        # Update the existing exclude rule with a newline
        $SED_INPLACE '/\[tool.poetry\]/,/^\[/{/exclude/{n;s/.*/"**\/\*.py"/}}' $PYPROJECT_TOML
    else
        # Add the exclude rule with a newline if it doesn't exist
        $SED_INPLACE '/\[tool.poetry\]/a\
exclude = ["**/*.py", ".venv/**", ".cache/**"]\
' $PYPROJECT_TOML
    fi

    # Step 2: Add or update the include rule under [tool.poetry]
    if grep -q '\[tool.poetry\]' $PYPROJECT_TOML && grep -A 5 '\[tool.poetry\]' $PYPROJECT_TOML | grep -q 'include'; then
        # Update the existing include rule with a newline
        $SED_INPLACE '/\[tool.poetry\]/,/^\[/{/include/{n;s/.*/"**\/\*.so", "**\/\*.pyi"/}}' $PYPROJECT_TOML
    else
        # Add the include rule with a newline if it doesn't exist
        $SED_INPLACE '/\[tool.poetry\]/a\
include = ["./*.so","'"$PACKAGE_NAME"'/*.pyi"]\
' $PYPROJECT_TOML
    fi

    echo "include and exclude rules added to $PYPROJECT_TOML"
}

# Function to remove include and exclude rules
remove_rules() {
    echo "Removing include and exclude rules..."

    # Step 1: Remove the exclude rule from pyproject.toml
    $SED_INPLACE '/exclude = \["\*\*\/\*\.py"\, "\.venv\/\*\*", "\.cache\/\*\*"]/d' $PYPROJECT_TOML

    # Step 2: Remove the include rule from pyproject.toml
    $SED_INPLACE '/include = \["\.\/\*\.so","'"$PACKAGE_NAME"'\/\*\.pyi"\]/d' "$PYPROJECT_TOML"

    echo "include and exclude rules removed from $PYPROJECT_TOML"
}
