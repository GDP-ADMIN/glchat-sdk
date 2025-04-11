# GDP Labs GenAI Plugin

## Description

A library to implement Plugin architecture and integrate with existing pipelines.

## Installation

1. Python v3.11 or above:

    You can install Python using [Miniconda](https://docs.anaconda.com/free/miniconda/index.html).

2. [Poetry](https://python-poetry.org/docs/) v1.8.2:

    You can install Poetry using cURL (you need Python to install Poetry):
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3. Install the library using Poetry:

    ```bash
    # Add GDP Labs artifact repository as primary source
    poetry source add gen-ai https://asia-southeast2-python.pkg.dev/gdp-labs/gen-ai/simple/ --priority=primary

    # Add PyPI as supplemental source
    poetry source add pypi --priority=supplemental

    # Authenticate to GDP Labs SDK libraries (only gat@gdplabs.id group team has access)
    poetry config http-basic.gen-ai oauth2accesstoken "$(gcloud auth print-access-token)"
    
    # Latest version
    poetry add gllm-plugin --source gen-ai

    # Specific version
    poetry add gllm-plugin@0.0.1b5 --source gen-ai
    ```

4. At this step, you can deactivate Miniconda environment as Poetry will create and manage its own virtual environment for you.
    ```bash
    conda deactivate
    ```

5. Try running the unit test to see if it's working:
    ```bash
    poetry run pytest
    ```

## Usage
For more information, please refer to the [PIPELINE.md](https://github.com/GDP-ADMIN/gen-ai-external/blob/main/libs/gllm-plugin/PIPELINE.md).
