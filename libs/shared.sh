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

# Function to configure Poetry authentication
configure_poetry_auth() {
    local token_file="${1:-token.key}"
    if [[ ! -f "$token_file" ]]; then
        echo "Error: Token file '$token_file' not found"
        return 1
    fi

    poetry config http-basic.gen-ai oauth2accesstoken "$(cat "$token_file")"
    poetry config http-basic.gen-ai-internal oauth2accesstoken "$(cat "$token_file")"
    poetry config http-basic.gen-ai-publication oauth2accesstoken "$(cat "$token_file")"
    poetry config http-basic.gen-ai-internal-publication oauth2accesstoken "$(cat "$token_file")"
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
        # Fixes building 'hnswlib' extension clang: error: unsupported argument 'native' to option '-march='
        # https://github.com/chroma-core/chroma/issues/221#issuecomment-1490362337
        export HNSWLIB_NO_NATIVE=1
        # Fixes macOS stuck at [keyring:keyring.backend] Loading macOS
        # https://github.com/python-poetry/poetry/issues/8623#issuecomment-1920957707
        export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
        brew install libmagic || :
        brew install ccache || :
        brew install gsed || :
        brew install cmake || :
        brew install coreutils || :
        brew install pkg-config || :
        brew install sentencepiece || :
        brew install protobuf || :
        brew install protobuf-c || :
        brew install cairo || :
        export PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:/opt/homebrew/lib/pkgconfig:$PKG_CONFIG_PATH"
        export DYLD_LIBRARY_PATH="/usr/local/lib:/opt/homebrew/lib:$DYLD_LIBRARY_PATH"
    elif [ "$RUNNER_OS" == "Windows" ]; then
        export PYTHONUTF8=1
    else
        apt-get install -y cmake
    fi
}

# Function to run pre-commit hooks
run_pre_commit() {
    local files="${1:-./}"
    poetry run pre-commit gc
    poetry run pre-commit run --files "$files"
}

# Function to run tests
run_coverage() {
  poetry run coverage run -m pytest --cov=. --cov-report=xml "$@" || [[ $? -eq 5 ]]
}

# Function to run tests with coverage
run_tests() {
    poetry run coverage run -m pytest --cov-report=xml --cov=. tests/ || [[ $? -eq 5 ]]
}

# Function to build with Nuitka
build_with_nuitka() {
    # Clean any existing build artifacts
    rm -rf build/ dist/ ./*.egg-info/ ./compilation-report.xml

    poetry run stubgen --include-docstrings -p "$1" -o .
    poetry build --format wheel --verbose

    if [ "$RUNNER_OS" == "macOS" ]; then
        # Wheel built on top of macos 15.0, below lines essential to support older versions
        ARCH=$(uname -m)
        wheel tags --remove --platform-tag="-macosx_$(sw_vers --productVersion | awk -F. '{print $1"_0"}')_${ARCH}" --platform-tag="+macosx_13_0_${ARCH}" "dist/$(ls dist/)"
    fi
}

# Function to install Poetry dependencies
install_dependencies() {
    max_retries=3
    count=0
    delay=5

    until poetry install --all-extras; do
    count=$((count + 1))
    if [ $count -ge $max_retries ]; then
        echo "Poetry install failed after $count attempts."
        exit 1
    fi
    echo "Poetry install failed. Retrying in $delay seconds... ($count/$max_retries)"
    sleep $delay
    done

    echo "Poetry install succeeded."
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
    # For lines NOT containing '-binary = {', append '-binary' to keys starting with 'gllm-' in table headers or keys
    # Before: [gllm-core]
    # After: [gllm-core-binary]
    sed '/-binary = {/!s/\(gllm-[a-zA-Z-]*\) = {\([^}]*\)}/\1-binary = {\2}/g' pyproject.toml

    # For lines NOT containing '-binary = {', append '-binary' to keys starting with 'bosa-' in table headers or keys
    # Before: [bosa-core]
    # After: [bosa-core-binary]
    sed '/-binary = {/!s/\(bosa-[a-zA-Z-]*\) = {\([^}]*\)}/\1-binary = {\2}/g' pyproject.toml

    # Replace source = "gen-ai-internal" with source = "gen-ai"
    # Before: source = "gen-ai-internal"
    # After: source = "gen-ai"
    sed 's/source = "gen-ai-internal"/source = "gen-ai"/g' pyproject.toml

    sed ':a;s/\(gllm-[a-zA-Z-]*\) = {[^}]*git = "[^"]*"[^}]*subdirectory = "[^"]*"[^}]*extras = \(\[[^]]*\]\)[^}]*rev = "[^"]*-v\([0-9]\+\.[0-9]\+\.[0-9]\+\)"[^}]*}/\1-binary = {version = "\3", source = "gen-ai", extras = \2}/g;ta' pyproject.toml
    sed ':a;s/\(gllm-[a-zA-Z-]*\) = {[^}]*git = "[^"]*"[^}]*subdirectory = "[^"]*"[^}]*rev = "[^"]*-v\([0-9]\+\.[0-9]\+\.[0-9]\+\)"[^}]*}/\1-binary = {version = "\2", source = "gen-ai"}/g;ta' pyproject.toml
    sed ':a;s/\(gllm-[a-zA-Z-]*\) = {[^}]*git = "[^"]*"[^}]*subdirectory = "[^"]*"[^}]*extras = \(\[[^]]*\]\)[^}]*}/\1-binary = {version = "*", source = "gen-ai", extras = \2}/g;ta' pyproject.toml
    sed ':a;s/\(gllm-[a-zA-Z-]*\) = {[^}]*git = "[^"]*"[^}]*subdirectory = "[^"]*"[^}]*}/\1-binary = {version = "*", source = "gen-ai"}/g;ta' pyproject.toml
    sed ':a;s/\(bosa-[a-zA-Z-]*\) = {[^}]*git = "[^"]*"[^}]*subdirectory = "[^"]*"[^}]*extras = \(\[[^]]*\]\)[^}]*rev = "[^"]*-v\([0-9]\+\.[0-9]\+\.[0-9]\+\)"[^}]*}/\1-binary = {version = "\3", source = "gen-ai", extras = \2}/g;ta' pyproject.toml
    sed ':a;s/\(bosa-[a-zA-Z-]*\) = {[^}]*git = "[^"]*"[^}]*subdirectory = "[^"]*"[^}]*rev = "[^"]*-v\([0-9]\+\.[0-9]\+\.[0-9]\+\)"[^}]*}/\1-binary = {version = "\2", source = "gen-ai"}/g;ta' pyproject.toml
    sed ':a;s/\(bosa-[a-zA-Z-]*\) = {[^}]*git = "[^"]*"[^}]*subdirectory = "[^"]*"[^}]*extras = \(\[[^]]*\]\)[^}]*}/\1-binary = {version = "*", source = "gen-ai", extras = \2}/g;ta' pyproject.toml
    sed ':a;s/\(bosa-[a-zA-Z-]*\) = {[^}]*git = "[^"]*"[^}]*subdirectory = "[^"]*"[^}]*}/\1-binary = {version = "*", source = "gen-ai"}/g;ta' pyproject.toml

    # Append '-binary' to package names in extras section, but only if they don't already have it
    # Before: cache = ["gllm-datastore"]
    # After: cache = ["gllm-datastore-binary"]
    # Also handles cases where package is already binary:
    # Before: cache = ["gllm-datastore-binary"]
    # After: cache = ["gllm-datastore-binary"] (unchanged)
    sed 's/\[\([^]]*\)\]/[\1]/g; s/"gllm-\([^"]*\)-binary"/"gllm-\1-binary"/g; s/"gllm-\([^"]*\)"/"gllm-\1-binary"/g; s/"bosa-\([^"]*\)-binary"/"bosa-\1-binary"/g; s/"bosa-\([^"]*\)"/"bosa-\1-binary"/g' pyproject.toml

    echo "Viewing pyproject.toml..."
    cat pyproject.toml
    echo "---"

    if poetry --version | grep -qE "Poetry \(version 2\.[0-9]+\.[0-9]+\)"; then
       poetry lock
    else
       poetry lock --no-update
    fi
}

printPackages() {
    local prefix="$1"

    for f in *
    do
        case $f in
            "$prefix"*) echo "$f";;
        esac
    done
}
