# VERSIONING.md

## Introduction
This document describes how the CI/CD pipeline determines the package version for each component within this project. The versioning is based on Git tags that adhere to a specific naming format.

## Important Note
The CI/CD pipeline utilizes the names of Git tags to designate the package version.

## Tag Name Standard
Git tag names should follow the format:

    <PACKAGE_NAME>-v<PEP_440_VERSIONS>

Where:
- `\<PACKAGE_NAME\>` refers to the name of the package.
- `\<PEP_440_VERSIONS\>` should conform to the semantic versioning standards set by [PEP 440](https://peps.python.org/pep-0440/).

## Versioning Standards
The CI/CD pipeline accepts package versions following the semantic versioning guidelines specified in PEP 440. 
- Versions must be formatted correctly to ensure they are parsed appropriately by the pipeline.
- This includes pre-release versions and post-release versions according to semantic versioning principles.

## Summary
To maintain coherence and reliability in version management through the CI/CD pipeline, all contributors should follow the specified tag naming conventions and ensure that version numbers comply with PEP 440 standards.
