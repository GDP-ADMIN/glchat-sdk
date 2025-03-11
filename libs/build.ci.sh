#!/bin/bash
set -e
# shellcheck source=/dev/null
source ../.ci/shared.sh

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
poetry config http-basic.gen-ai-internal oauth2accesstoken "$(cat token.key)"

# Use binary version
update_pyproject
poetry install --all-extras --with compiler
poetry add libmagic python-magic-bin
poetry run pre-commit run
poetry run coverage run -m pytest --cov-report=xml --cov=. tests/
binary_build
