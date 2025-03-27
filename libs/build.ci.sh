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

# Package Installation
poetry install --all-extras --with compiler
if [ "$RUNNER_OS" == "Windows" ]; then
  poetry add python-magic-bin libmagic
elif [[ "$RUNNER_OS" == "macOS" ]]; then
  brew install libmagic
fi

poetry run pre-commit run --files ./
poetry run coverage run -m pytest --cov-report=xml --cov=. tests/
poetry run stubgen --include-docstrings -p "${MODULE//-/_}" -o .

# Nuitka build backend read version from setup.cfg only, otherwise 0.0.0.
cat <<EOF > setup.cfg
[metadata]
version = $(poetry version -s)
EOF

poetry build --format wheel --verbose
