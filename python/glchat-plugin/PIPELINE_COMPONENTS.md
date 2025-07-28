### Pipeline Components

This section will guide you about pipeline components and how to customize them.

#### Pipeline File Structure

```sh
<pipeline-name>
├── __init__.py
├── config.yaml
├── pipeline.py
├── preset_config.py
└── state.py
```

1. `pipeline.py`
    This is the pipeline entry point. It will define the steps of the pipeline and how they interact with each other. The class must implements `PipelineBuilderPlugin[State, PresetConfig]`. This file needs to be named `pipeline.py` and must not be moved.

2. `preset_config.py`
    This is the preset configuration for the pipeline. This configuration will include any parameters needed to initialize the pipeline.

3. `state.py`
    This is the state for the pipeline. This state will hold the necessary data throughout the pipeline's execution.

4. `config.yaml`
    This is the configuration for the pipeline. It will define the configuration for the pipeline.
    The config.yaml contains following:
    - `rago_pipeline`: The name of the pipeline. It must match the name in `pipeline.py`.
    - `presets`: The list of preset configurations. Each preset must contain config keys: `pipeline_preset_id`, `supported_models`, and all keys defined in `preset_config.py`. Optionally, the config keys can also contain keys in `BasePipelinePresetConfig` to override the default values. The following are the optional keys with their default values:
      - `supported_agents: list[str] = []`
      - `support_pii_anonymization: bool = False`
      - `support_multimodal: bool = True`
      - `use_docproc: bool = True`
      - `search_types: list[SearchType] = [normal]`
    - `chatbots`: The list of chatbot configurations. Each chatbot must contains following keys:
      - `id`
      - `display_name`
      - `description`
      - `pipeline_preset_id`: use 1 of the pipeline_preset_id defined in presets
      - `prompt_builder_catalogs`: Prompt builder catalogs
      - `lmrp_catalogs`: LMRP catalogs
    - `user_chatbots`: The list of user chatbots.

5. `__init__.py`
    This is the initialization file for the pipeline module.


Note that `pipeline.py` and `config.yaml` files must be named as such and must not be moved.
Other files can be named as per your preference and can be placed in any directory.
Make sure to add `__init__.py` to all new directories to able to import the module.
