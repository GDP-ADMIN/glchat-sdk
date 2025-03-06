# GDP Labs GenAI Plugin

## Description

A library to implement Plugin architecture and integrate with existing pipelines.

## Installation

1. Python v3.11 or above:

    You can install Python using [Miniconda](https://docs.anaconda.com/free/miniconda/index.html).

2. [Poetry](https://python-poetry.org/docs/) v1.8.1 or above:

    You can install Poetry using cURL (you need Python to install Poetry):
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3. Install the library using Poetry:
    ```bash
    # Latest
    poetry add "git+ssh://git@github.com/GDP-ADMIN/gen-ai-internal.git#subdirectory=libs/gllm-plugin"

    # Specific version
    poetry add "git+ssh://git@github.com/GDP-ADMIN/gen-ai-internal.git@gllm_plugin-v0.0.1#subdirectory=libs/gllm-plugin"
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
For more information, please refer to the [PIPELINE.md](https://gdp-admin.github.io/gen-ai-internal/gllm-plugin/PIPELINE.md).
