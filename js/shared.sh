#!/bin/bash
# shellcheck disable=SC2086,SC2064,SC2155

# Common configuration and utility functions for build scripts
# This file should be sourced in other build scripts
if [[ "$RUNNER_OS" == "macOS" ]]; then
    sed(){
        command gsed -i "$@"
    }
else
    sed(){
        command sed -i "$@"
    }
fi

# Function to configure build files
configure_build_files() {
    local version="$1"
    npm version "$version" --no-git-tag-version
}

# Function to run tests with coverage
run_tests() {
    npm run lint
    npm run test:coverage
}

# Function to install Node.js dependencies
install_dependencies() {
    max_retries=3
    count=0
    delay=5

    # Try npm install first, then fallback to other package managers
    until npm ci || npm install; do
        count=$((count + 1))
        if [ $count -ge $max_retries ]; then
            echo "npm install failed after $count attempts."
            exit 1
        fi

        echo "npm install failed. Retrying in $delay seconds... ($count/$max_retries)"
        sleep $delay
    done

    echo "npm install succeeded."
}

# Function to convert package name from kebab-case to camelCase
convert_to_camel_case() {
    local folder_name="$1"
    echo "$folder_name" | sed 's/-\([a-z]\)/\U\1/g'
}

# Function to convert package name from camelCase to kebab-case
convert_to_kebab_case() {
    local folder_name="$1"
    echo "$folder_name" | sed 's/\([A-Z]\)/-\L\1/g' | sed 's/^-//'
}

# Function to convert package name from kebab-case to PascalCase
convert_to_pascal_case() {
    local folder_name="$1"
    echo "$folder_name" | sed 's/-\([a-z]\)/\U\1/g' | sed 's/^\([a-z]\)/\U\1/'
}

build() {
    npm run build
    npm pack
}
