#!/bin/bash
# shellcheck disable=SC2086,SC2064,SC2155

# Common configuration and utility functions for build scripts
# This file should be sourced in other build scripts

# Function to configure Poetry authentication
configure_poetry_auth() {
    local token_file="${1:-token.key}"
    if [[ ! -f "$token_file" ]]; then
        echo "Error: Token file '$token_file' not found"
        return 1
    fi

    poetry config http-basic.gen-ai oauth2accesstoken "$(cat "$token_file")"
    poetry config http-basic.gen-ai-publication oauth2accesstoken "$(cat "$token_file")"
}

# Function to configure build files
configure_build_files() {
    local version="$1"
    if ! grep -q "\[tool.poetry.build\]" pyproject.toml; then
        cat <<EOF >> "pyproject.toml"

[tool.poetry.build]
script = "build.py"
generate-setup-file = true

[build-system]
requires = [
    "setuptools==75.9.1",
    "wheel==0.45.1",
    "nuitka==2.6.9",
    "toml==0.10.2"
]
build-backend = "nuitka.distutils.Build"
EOF
    fi

    cat <<EOF > setup.py
from setuptools import setup

if __name__ == "__main__":
    setup(build_with_nuitka=True)
EOF

    # update package version
    poetry version $version
}

# Function to install system dependencies based on OS
install_system_dependencies() {
    if [ "$RUNNER_OS" == "macOS" ]; then
        brew install libmagic
        brew install ccache
        brew install gsed
    fi
}

# Function to run pre-commit hooks
run_pre_commit() {
    local files="${1:-./}"
    poetry run pre-commit gc
    poetry run pre-commit run --files "$files"
}

# Function to run tests with coverage
run_tests() {
    poetry run coverage run -m pytest --cov-report=xml --cov=. tests/ || [[ $? -eq 5 ]]
}

# Function to build with Nuitka
build_with_nuitka() {
    poetry run stubgen --include-docstrings -p "$1" -o .
    poetry build --format wheel --verbose
}

# Function to install Poetry dependencies
install_dependencies() {
    poetry config installer.parallel false
    poetry install --all-extras
}

# Function to convert package name from kebab-case to snake_case
convert_to_snake_case() {
    local folder_name="$1"
    echo "$folder_name" | tr '-' '_'
} 

# Function to convert package name from snake_case to kebab-case
convert_to_kebab_case() {
    local folder_name="$1"
    echo "$folder_name" | tr '_' '-'
}

# Function to modify pyproject.toml for binary builds
modify_pyproject_toml() {
    local package_name="$1"
    local binary_package_name="${package_name}-binary"
    
    if [[ "$RUNNER_OS" == "macOS" ]]; then
        EXEC_COMMAND="gsed"
    else
        EXEC_COMMAND="sed"
    fi

    "$EXEC_COMMAND" -i "s/name = \"$package_name\"/name = \"$binary_package_name\"/" pyproject.toml
    "$EXEC_COMMAND" -i "s/gllm-\([a-zA-Z-]*\) = {git = \"ssh:\/\/git@github.com\/GDP-ADMIN\/gen-ai-internal.git\", subdirectory = \"libs\/gllm-\1\"\(, [^}]*\)\?}/gllm-\1-binary = {version = \"*\"\2}/g" pyproject.toml
    "$EXEC_COMMAND" -i "s/bosa-\([a-zA-Z-]*\) = {git = \"ssh:\/\/git@github.com\/GDP-ADMIN\/gen-ai-internal.git\", subdirectory = \"libs\/bosa-\1\"\(, [^}]*\)\?}/bosa-\1-binary = {version = \"*\"\2}/g" pyproject.toml
    
    poetry lock --no-update
}
