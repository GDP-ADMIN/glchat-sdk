#!/bin/bash

if [ -n "${TAG_NAME}" ]; then
    # Publish to Google Artifact Registry
    poetry config http-basic.gen-ai-publication oauth2accesstoken "$(cat token.key)"
    poetry publish --repository gen-ai-publication --skip-existing

    # Publish to PyPI
    poetry publish --skip-existing
else
    echo "No release tag detected. Skipping binary upload."
fi
