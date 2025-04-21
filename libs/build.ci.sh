#!/bin/bash
set -e

# Check if at least one package folder name is provided
if [ "$#" -ne 1 ]; then
  echo "Error: No package folder names provided."
  echo "Usage: ./build.local.sh <package_name>"
  exit 1
fi

cd "$MODULE"

# Git Authentication
git config --unset credential.helper || :
git config --global user.username "infra-gl"
git config --global user.email "gdplabs@gdplabs.id"
git config --global url."https://${GH_TOKEN}:x-oauth-basic@github.com/".insteadOf "https://github.com/"
git config --global url."https://${GH_TOKEN}:x-oauth-basic@github.com".insteadOf "ssh://git@github.com"

# Google Cloud Authentication
poetry config http-basic.gen-ai oauth2accesstoken "$(cat token.key)"
poetry config http-basic.gen-ai-publication oauth2accesstoken "$(cat token.key)"

# If we put below code in pyproject.toml, when developers installing this package with Git, the package will be built as binary (Nuitka).
cat <<EOF >> "pyproject.toml"

[tool.poetry.build]
script = "build.py"
generate-setup-file = true

[build-system]
requires = ["setuptools", "wheel", "nuitka", "toml"]
build-backend = "nuitka.distutils.Build"
EOF

cat <<EOF > setup.py
from setuptools import setup

if __name__ == "__main__":
    setup(build_with_nuitka=True)
EOF

# Nuitka build backend read version from setup.cfg only, otherwise 0.0.0.
cat <<EOF > setup.cfg
[metadata]
version = $(poetry version -s)
EOF

# Build Dependency Installation
if [ "$RUNNER_OS" == "Windows" ]; then
  poetry add python-magic-bin libmagic
elif [[ "$RUNNER_OS" == "macOS" ]]; then
  brew install libmagic
  brew install ccache
  brew install gsed
  # override sed with gsed
  sed() { gsed "$@"; }
fi

MODULE_BINARY_NAME="${MODULE}-binary"

sed -i "s/name = \"$MODULE\"/name = \"$MODULE_BINARY_NAME\"/" pyproject.toml
sed -i "s/gllm-\([a-zA-Z-]*\) = {git = \"ssh:\/\/git@github.com\/GDP-ADMIN\/gen-ai-internal.git\", subdirectory = \"libs\/gllm-\1\"\(, [^}]*\)\?}/gllm-\1-binary = {version = \"*\", source = \"gen-ai\"\2}/g" pyproject.toml
sed -i "s/bosa-\([a-zA-Z-]*\) = {git = \"ssh:\/\/git@github.com\/GDP-ADMIN\/gen-ai-internal.git\", subdirectory = \"libs\/bosa-\1\"\(, [^}]*\)\?}/bosa-\1-binary = {version = \"*\", source = \"gen-ai\"\2}/g" pyproject.toml

poetry lock --no-update

# Package Installation
poetry install --all-extras --with compiler

poetry run pre-commit run --files ./
poetry run coverage run -m pytest --cov-report=xml --cov=. tests/
poetry run stubgen --include-docstrings -p "${MODULE//-/_}" -o .

poetry build --format wheel --verbose
