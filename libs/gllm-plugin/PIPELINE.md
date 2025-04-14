### Add new Pipeline to GLLM Backend

This example will guide you through creating new pipeline classes from an external repository and integrating them into GLChat.

1. **Add [`gllm-plugin`](https://console.cloud.google.com/artifacts/python/gdp-labs/asia-southeast2/gen-ai/gllm-plugin?project=gdp-labs) dependency in `pyproject.toml`**

    ```sh
    # Add GDP Labs artifact repository as primary source
    poetry source add gen-ai https://asia-southeast2-python.pkg.dev/gdp-labs/gen-ai/simple/ --priority=primary

    # Add PyPI as supplemental source
    poetry source add pypi --priority=supplemental

    # Authenticate to GDP Labs SDK libraries (Only gat@gdplabs.id group team has access)
    poetry config http-basic.gen-ai oauth2accesstoken "$(gcloud auth print-access-token)"

    # Latest version
    poetry add gllm-plugin --source gen-ai

    # Specific version
    poetry add gllm-plugin@0.0.1b5 --source gen-ai
    ```

2. **Define the Pipeline State**

    Create a new file `state.py` and define the state for your new pipeline (e.g., `NewState`). This state will hold the necessary data throughout the pipeline's execution.

3. **Define the Pipeline Preset Configuration**

    Create a new file `preset_config.py` and define the preset configuration for your new pipeline (e.g., `NewPresetConfig`). This configuration will include any parameters needed to initialize the pipeline.

4. **Implement the Pipeline Builder**

    Create a new file `pipeline.py` that implements `PipelineBuilderPlugin[NewState, NewPresetConfig]`. This class will define the steps of the pipeline and how they interact with each other.

5. **Define the Pipeline Configurations**

    Create a new file `config.yaml` and define the config for your new pipeline.
    The `config.yaml` contains following:
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
      - `lmrp_catalogs`:
        - `name: generate_conversation_title` 
        - `scope: openai`
        - `prompt_builder_type: agnostic`
        - `prompt_builder_kwargs`
        - `prompt_builder_system_template` 
        - `prompt_builder_user_template` 
        - `lm_invoker_type: openai`
        - `lm_invoker_kwargs: |
          {
            "model_name": "gpt-4o-mini"
          }`
        - `lm_invoker_env_kwargs: |
          {
            "api_key": "OPENAI_API_KEY"
          }`
        - `output_parser_type: none`
        - `output_parser_kwargs`
    - `user_chatbots`: The list of user chatbots.

6. **Refer to the Example Repository**

    You can find an example of a simple pipeline implementation in the following repository: [gen-ai-examples/simple-pipeline](https://github.com/GDP-ADMIN/gen-ai-examples/tree/main/examples/simple-pipeline). 

7. **Register the new pipeline to GLLM Backend using API.**

    Sample curl request:
    ```sh
    curl --request POST \
    --url http://localhost:8000/register-pipeline-plugin \
    --header 'Content-Type: application/json' \
    --data '{
        "folder_name": "simple_pipeline",
        "path": "/Users/username/Downloads/simple-pipeline"
    }'
    ```

    The project structure will be as follows:
    ```
    simple-pipeline [git folder]
    ├── pyproject.toml [depends on gllm-plugin]
    └── simple_pipeline/
        ├── config.yaml
        ├── pipeline.py
        ├── preset_config.py
        └── state.py
    ```

    After following these steps, you can now use the new pipeline in GLChat.

8. **Testing the New Pipeline in GLChat**

    After registering the new pipeline, follow these steps to verify that it is active:

    - Log in to GLChat using a user account assigned to a chatbot that uses the new pipeline.
    - Check the available chatbots — you should see a chatbot configured with the new pipeline based on `config.yaml`.
    - Interact with the chatbot to ensure that it responds using the registered pipeline.

    This confirms that the new pipeline has been successfully integrated into GLChat.
