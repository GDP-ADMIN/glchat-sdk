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

    Create a new file `state.py` and define the state for your new pipeline (e.g., NewState). This state will hold the necessary data throughout the pipeline's execution.

3. **Define the Pipeline Preset Configuration**

    Create a new file `preset_config.py` and define the preset configuration for your new pipeline (e.g., NewPresetConfig). This configuration will include any parameters needed to initialize the pipeline.

4. **Implement the Pipeline Builder**

    Create a new file `pipeline.py` that implements `PipelineBuilderPlugin[NewState, NewPresetConfig]`. This class will define the steps of the pipeline and how they interact with each other.

5. **Define the Pipeline Configurations**

    Create a new file `config.yaml` and define the config for your new pipeline.
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
      - `inference_catalog`: path to catalog Google spreadsheet. The spreadsheet needs to allow access from GLChat Google account.
        - `sheet_id`
        - `prompt_builder_worksheet_id`
        - `lmrp_worksheet_id`
    - `user_chatbots`: The list of user chatbots.

6. **Define the Pipeline Environment**

    Create a new file `.env` and define the env key value for your pipeline.
    Add prefix to all env keys to prevent clash with other pipelines.

7. **Register the new pipeline to GLLM Backend using API.**

    The project structure will be as follows:
    ```
    - simple-pipeline [git folder]
    - pyproject.toml [depends on gllm-plugin]
    - simple_pipeline
        - .env
        - config.yaml
        - pipeline.py
        - preset_config.py
        - state.py
    ```

    Zip the project and register it to GLChat.

    Sample curl request:
    ```sh
    curl --request POST \
    --url http://localhost:8000/register-pipeline-plugin \
    --header 'Content-Type: multipart/form-data' \
    --form 'zip_file=@/path_to_pipeline/simple-pipeline.zip'
    ```

    After following these steps, you can now use the new pipeline in GLChat.

8. **Testing the New Pipeline in GLChat**

    After registering the new pipeline, follow these steps to verify that it is active:

    - Log in to GLChat using a user account assigned to a chatbot that uses the new pipeline.
    - Check the available chatbots — you should see a chatbot configured with the new pipeline based on config.yaml.
    - Interact with the chatbot to ensure that it responds using the registered pipeline.

    This confirms that the new pipeline has been successfully integrated into GLChat.
    
`state.py`
```python
from enum import StrEnum
from typing import Any, TypedDict

from gllm_core.event.event_emitter import EventEmitter


class SimpleState(TypedDict):
    """A TypedDict representing the state of the Simple Pipeline.

    Attributes:
        response_synthesis_bundle (dict[str, Any]): The bundle of response synthesis.
        response (str): The generated response to the user's query.
    """

    response_synthesis_bundle: dict[str, Any]
    response: str



class SimpleStateKeys(StrEnum):
    """List of all possible keys in SimpleState."""

    RESPONSE_SYNTHESIS_BUNDLE = "response_synthesis_bundle"
    RESPONSE = "response"
```

`preset_config.py`
```python
from gllm_plugin.config.base_pipeline_preset_config import BasePipelinePresetConfig

class SimplePresetConfig(BasePipelinePresetConfig):
    """A Pydantic model representing the preset config of the Simple Pipeline.

    Inherits attributes from `BasePipelinePresetConfig`.

    Attributes:
        None
    """
```

`pipeline.py`
```python
from typing import Any

from gllm_generation.response_synthesizer import StaticListResponseSynthesizer
from gllm_pipeline.pipeline.pipeline import Pipeline
from gllm_pipeline.steps import step
from gllm_plugin.pipeline.pipeline_plugin import PipelineBuilderPlugin

from new_repository.config.pipeline.simple.preset_config import SimplePresetConfig
from new_repository.config.pipeline.simple.state import SimpleState, SimpleStateKeys


class SimplePipelineBuilder(PipelineBuilderPlugin[SimpleState, SimplePresetConfig]):
    """The Simple Pipeline Builder.

    This pipeline will simply pass the user query to the response synthesizer.
    There are no prompt templates used in this pipeline.

    Inherits attributes from `PipelineBuilder`.
    """

    name = "simple-pipeline"
    preset_config_class = SimplePresetConfig

    def __init__(self):
        """Initialize the Simple Pipeline Builder."""
        super().__init__()

    async def build(self, pipeline_config: dict[str, Any]) -> Pipeline:
        """Build the pipeline.

        Args:
            pipeline_config (dict[str, Any]): The pipeline configuration.

        Returns:
            Pipeline: The Simple Pipeline.
        """
        response_synthesizer_step = step(
            component=self.build_response_synthesizer(),
            input_state_map={
                "state_variables": SimpleStateKeys.RESPONSE_SYNTHESIS_BUNDLE
            },
            output_state=SimpleStateKeys.RESPONSE,
        )

        pipeline = Pipeline(
            steps=[
                response_synthesizer_step,
            ],
            state_type=SimpleState,
        )

        return pipeline

    def build_initial_state(self, request: dict[str, Any], pipeline_config: dict[str, Any], **kwargs: Any) -> SimpleState:
        """Build the initial state for pipeline invoke.

        Args:
            request (dict[str, Any]): The given request from the user.
            pipeline_config (dict[str, Any]): The pipeline configuration.
            **kwargs (Any): A dictionary of arguments required for building the initial state.

        Returns:
            SimpleState: The initial state.
        """
        return SimpleState(
            response_synthesis_bundle={"context_list": [f"Re: {request.get("message")}"]}
        )

    def build_response_synthesizer(self) -> StaticListResponseSynthesizer:
        """Build the response synthesizer component.

        Args:
            None

        Returns:
            StaticListResponseSynthesizer: The response synthesizer component.
        """
        return StaticListResponseSynthesizer()
```

`config.yaml`
```yaml
rago_pipeline: simple-pipeline


presets:
  - pipeline_preset_id: preset-1
    supported_models:
      - anthropic/claude-3-5-sonnet
      - openai/gpt-4o-mini
      - openai/gpt-4o
    support_multimodal: true
    use_docproc: false

  - pipeline_preset_id: preset-2
    supported_models:
      - openai/gpt-4o
      - openai/gpt-4o-mini
    support_multimodal: false
    use_docproc: false


chatbots:
  - id: simple-chatbot-1a
    display_name: Simple Chatbot 1a
    description: A chatbot using the preset 1
    pipeline_preset_id: preset-1
    inference_catalog:
      sheet_id: "1X5g3Ruetgg27ybRZ7ie40oxXzbS4YLqRP5_rpQ7MYps"
      prompt_builder_worksheet_id: "0"
      lmrp_worksheet_id: "1151817216"

  - id: simple-chatbot-1b
    display_name: Simple Chatbot 1b
    description: Another chatbot using the preset 1
    pipeline_preset_id: preset-1
    inference_catalog:
      sheet_id: "1X5g3Ruetgg27ybRZ7ie40oxXzbS4YLqRP5_rpQ7MYps"
      prompt_builder_worksheet_id: "0"
      lmrp_worksheet_id: "1151817216"

  - id: simple-chatbot-2
    display_name: Simple Chatbot 2
    description: A chatbot using the preset 2
    pipeline_preset_id: preset-2
    inference_catalog:
      sheet_id: "1X5g3Ruetgg27ybRZ7ie40oxXzbS4YLqRP5_rpQ7MYps"
      prompt_builder_worksheet_id: "0"
      lmrp_worksheet_id: "1151817216"


user_chatbots:
  - user_id: user-new-1
    chatbot_ids:
      - simple-chatbot-1a
      - simple-chatbot-1b

  - user_id: user-new-2
    chatbot_ids:
      - "*"
```

`.env`
```
SIMPLE_PIPELINE_ENV_KEY_1=value1
SIMPLE_PIPELINE_ENV_KEY_2=value2
```
