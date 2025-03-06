#!/bin/bash
set -e


# shellcheck source=/dev/null
# Note: Shellcheck don't have access to the file because it's an external file.
# https://www.shellcheck.net/wiki/SC1091

source ../shared.sh

# Git Authentication
git config --unset credential.helper || :
git config --global user.username "infra-gl"
git config --global user.email "gdplabs@gdplabs.id"
git config --global url."https://${GH_TOKEN}:x-oauth-basic@github.com/".insteadOf "https://github.com/"
git fetch --unshallow || :
git fetch origin "${BASE_BRANCH}"

update_pyproject

set -xe

poetry install --all-extras --with compiler

REPORT_PATH=build/reports
mkdir -p $REPORT_PATH

# Pre-commit
CHANGED_FILES=$(git diff --name-only --relative "origin/${BASE_BRANCH}...HEAD" .)
poetry run pre-commit gc

# shellcheck disable=SC2086
poetry run pre-commit run --files $CHANGED_FILES

# Pytest
poetry run coverage run -m pytest tests/unit_tests/
poetry run coverage report -m --skip-empty
poetry run coverage xml -i -o $REPORT_PATH/gdplabs-gen-ai.xml

# Build Binary
if [[ "$TAG_NAME" != "notag" ]]; then
    binary_build
fi
