### Add new Pipeline to GLLM Backend

This example will guide you through creating new pipeline classes from external repository and integrate in GLChat.

1. **Add `gllm-plugin` dependency in `pyproject.toml`**

    ```toml
    gllm-plugin = {git = "ssh://git@github.com/GDP-ADMIN/gen-ai-internal.git", subdirectory = "libs/gllm-plugin"}
    ```

2. **Define the Pipeline State**

    Create a new file `state.py` and define the state for your new pipeline. This state will hold the necessary data throughout the pipeline's execution.

3. **Define the Pipeline Preset Configuration**

    Create a new file `preset_config.py` and define the preset configuration for your new pipeline. This configuration will include any parameters needed to initialize the pipeline.

4. **Implement the Pipeline Builder**

    Create a new file `pipeline.py` that implements `PipelineBuilderPlugin[NewState, NewPresetConfig]`. This class will define the steps of the pipeline and how they interact with each other.

5. **Add new pipeline to GLLM Backend dependency manager and register using `PluginManager`.**
First, add the new pipeline to the `gllm_backend` dependency manager in the `pyproject.toml` file.
```toml
new-pipeline = {git = "ssh://git@github.com/new-pipeline", subdirectory = "/"}
```

The project structure will be as follows:
```
- gen-ai-template [git folder]
  - applications
    - gdplabs-gen-ai-starter-gllm-backend
      - pyproject.toml [add dependency to folder /full/path/to/claudia-rag]

- claudia-pipeline-repo [git folder]
  - pyproject.toml [depends on gllm-plugin]
  - pipeline
    - claudia-rag
      - pipeline.py
      - state.py
      - config.py
```

After following these steps, you can now use the new pipeline in GLChat by adding it to the pipeline configuration using import.
```python
from new_repository.config.pipeline.simple.preset_config import SimplePresetConfig
from new_repository.config.pipeline.simple.state import SimpleState, SimpleStateKeys
```


### Example Usage for Static Response Synthesizer
`state.py`
```python
from enum import StrEnum
from typing import Any, TypedDict

from gllm_core.event.event_emitter import EventEmitter


class SimpleState(TypedDict):
    """A TypedDict representing the state of a Simple pipeline.

    Attributes:
        event_emitter (EventEmitter): An event emitter instance.
        user_query (str): The original query from the user.
        response (str): The generated response to the user's query.
    """

    event_emitter: EventEmitter
    user_query: str
    response: str
    response_synthesis_bundle: dict[str, Any]


class SimpleStateKeys(StrEnum):
    """List of all possible keys in NoOpState."""

    EVENT_EMITTER = "event_emitter"
    USER_QUERY = "user_query"
    RESPONSE = "response"
    RESPONSE_SYNTHESIS_BUNDLE = "response_synthesis_bundle"
```

`preset.py`
```python
from gllm_plugin.config.base_pipeline_preset_config import BasePipelinePresetConfig

class SimplePresetConfig(BasePipelinePresetConfig):
    """A Pydantic model representing the preset config of a Simple pipeline.

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
    """Simple pipeline builder.

    This pipeline will simply pass the user query to the response synthesizer.
    There are no prompt templates used in this pipeline.

    Inherits attributes from `PipelineBuilder`.
    """

    name = "simple"
    preset_config_class = SimplePresetConfig

    def __init__(self):
        """Initialize the simple pipeline builder."""
        super().__init__()

    def build(self, pipeline_config: dict[str, Any]) -> Pipeline:
        """Build the pipeline.

        Args:
            pipeline_config (dict[str, Any]): The pipeline configuration.

        Returns:
            Pipeline: The simple pipeline.
        """
        response_synthesizer_step = step(
            component=self.build_response_synthesizer(),
            input_state_map={
                "query": SimpleStateKeys.USER_QUERY,
                "event_emitter": SimpleStateKeys.EVENT_EMITTER,
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
            event_emitter=kwargs.get("event_emitter"),
            user_query=request.get("message"),
            response="",
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
