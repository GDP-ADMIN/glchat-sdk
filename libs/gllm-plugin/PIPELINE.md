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

### Example Usage with Call LLM and Use Chat History
`state.py`
```python
from enum import StrEnum
from typing import Any, TypedDict

from gllm_core.event.event_emitter import EventEmitter


class NoOpState(TypedDict):
    """A TypedDict representing the state of a No-op pipeline.

    Attributes:
        event_emitter (EventEmitter): An event emitter instance.
        history (list[tuple[str, list[Any]]]): The conversation history.
        user_query (str): The original query from the user.
        response (str): The generated response to the user's query.
    """

    event_emitter: EventEmitter
    history: list[tuple[str, list[Any]]]
    user_query: str
    response: str


class NoOpStateKeys(StrEnum):
    """List of all possible keys in NoOpState."""

    EVENT_EMITTER = "event_emitter"
    HISTORY = "history"
    USER_QUERY = "user_query"
    RESPONSE = "response"
```

`config.py`
```python
from enum import StrEnum

class SearchType(StrEnum):
    """The type of search to perform.

    Values:
        NORMAL: Get answer from chatbot knowledge.
        SMART: Get more relevant information from your stored documents and knowledge base.
            Knowledge Search is an AI with specialized knowledge. No agents are available in this mode.
        WEB: Get more relevant information from the web.
            Web Search uses real-time data. Agent selection isn't available in this mode.
    """

    NORMAL = "normal"
    SMART = "smart"
    WEB = "web"

from typing import Any
from pydantic import BaseModel

class BasePipelinePresetConfig(BaseModel):
    """A Pydantic model representing the base preset configuration of all pipelines.

    Attributes:
        pipeline_preset_id (str): The pipeline preset id.
        supported_models (dict[str, Any]): The supported models.
        supported_agents (list[dict[str, Any]]): The supported agents.
        support_pii_anonymization (bool): Whether the pipeline supports pii anonymization.
        support_multimodal (bool): Whether the pipeline supports multimodal.
        use_docproc (bool): Whether to use the document processor.
        search_types (list[SearchType]): The supported search types.
    """

    pipeline_preset_id: str
    supported_models: dict[str, Any]
    supported_agents: list[dict[str, Any]]
    support_pii_anonymization: bool
    support_multimodal: bool
    use_docproc: bool
    search_types: list[SearchType]

from pydantic import Field

class NoOpPresetConfig(BasePipelinePresetConfig):
    """A Pydantic model representing the preset config of a No-op pipeline.

    Inherits attributes from `BasePipelinePresetConfig`.

    Attributes:
        chat_history_limit (int): The chat history limit. Must be greater than or equal to 0.
    """

    chat_history_limit: int = Field(ge=0)
```

`pipeline.py`
```python
from typing import Any

from gllm_generation.response_synthesizer import StuffResponseSynthesizer
from gllm_pipeline.pipeline.pipeline import Pipeline
from gllm_pipeline.steps import step
from gllm_plugin.pipeline.pipeline_plugin import PipelineBuilderPlugin
from gdplabs_gen_ai_starter_gllm_backend.config.pipeline.no_op.state import NoOpStateKeys as StateKeys
from gdplabs_gen_ai_starter_gllm_backend.chat_history import ChatHistoryStorage
from gdplabs_gen_ai_starter_gllm_backend.component import ChatHistoryManager
from gdplabs_gen_ai_starter_gllm_backend.config.constant import DEFAULT_MODEL
from gdplabs_gen_ai_starter_gllm_backend.config.pipeline.general_pipeline_config import GeneralPipelineConfigKeys
from gdplabs_gen_ai_starter_gllm_backend.config.pipeline.no_op.preset_config import NoOpPresetConfig
from gdplabs_gen_ai_starter_gllm_backend.config.pipeline.no_op.state import NoOpState
from gdplabs_gen_ai_starter_gllm_backend.config.pipeline.pipeline_helper import build_save_history_step
from gdplabs_gen_ai_starter_gllm_backend.config.supported_models import UNIMODAL_PROVIDERS, ModelName
from gdplabs_gen_ai_starter_gllm_backend.utils.initializer import get_lm_invoker


class NoOpPipelineBuilder(PipelineBuilderPlugin[NoOpState, NoOpPresetConfig]):
    """No-op pipeline builder.

    This pipeline will simply pass the user query to the response synthesizer.
    There are no prompt templates used in this pipeline.

    Inherits attributes from `PipelineBuilder`.
    """

    name = "no-op"
    chat_history_storage: ChatHistoryStorage
    preset_config_class = NoOpPresetConfig

    def __init__(self):
        """Initialize the no-op pipeline builder."""
        self.chat_history_manager = ChatHistoryManager(storage=self.chat_history_storage)

    def build(self, pipeline_config: dict[str, Any]) -> Pipeline:
        """Build the pipeline.

        Args:
            pipeline_config (dict[str, Any]): The pipeline configuration.

        Returns:
            Pipeline: The no-op pipeline.
        """
        model_name = pipeline_config.get("model_name", ModelName.from_string(DEFAULT_MODEL))

        multimodality = pipeline_config.get("support_multimodal", False)

        retrieve_history_step = step(
            component=self.chat_history_manager,
            input_state_map={},
            output_state=StateKeys.HISTORY,
            runtime_config_map={
                ChatHistoryManager.USER_ID_KEY: GeneralPipelineConfigKeys.USER_ID,
                ChatHistoryManager.CONVERSATION_ID_KEY: GeneralPipelineConfigKeys.CONVERSATION_ID,
                ChatHistoryManager.CHAT_HISTORY_KEY: GeneralPipelineConfigKeys.CHAT_HISTORY,
            },
            fixed_args={
                ChatHistoryManager.OPERATION_KEY: ChatHistoryManager.OP_READ,
                ChatHistoryManager.LIMIT_KEY: pipeline_config.get("chat_history_limit"),
                ChatHistoryManager.IS_MULTIMODAL_KEY: multimodality,
            },
        )

        response_synthesizer_config = (
            {}
            if model_name.provider in UNIMODAL_PROVIDERS
            else {"user_multimodal_contents": GeneralPipelineConfigKeys.BINARIES}
        )

        response_synthesizer_step = step(
            component=self.build_response_synthesizer(model_name),
            input_state_map={
                "query": StateKeys.USER_QUERY,
                "history": StateKeys.HISTORY,
                "event_emitter": StateKeys.EVENT_EMITTER,
            },
            output_state=StateKeys.RESPONSE,
            runtime_config_map=response_synthesizer_config,
        )

        save_history_step = build_save_history_step(chat_history_manager=self.chat_history_manager)

        pipeline = Pipeline(
            steps=[
                retrieve_history_step,
                response_synthesizer_step,
                save_history_step,
            ],
            state_type=NoOpState,
        )

        return pipeline

    def build_initial_state(self, request: dict[str, Any], pipeline_config: dict[str, Any], **kwargs: Any) -> NoOpState:
        """Build the initial state for pipeline invoke.

        Args:
            request (dict[str, Any]): The given request from the user.
            pipeline_config (dict[str, Any]): The pipeline configuration.
            **kwargs (Any): A dictionary of arguments required for building the initial state.

        Returns:
            NoOpState: The initial state.
        """
        return NoOpState(
            event_emitter=kwargs.get("event_emitter"),
            history=[],
            user_query=request.get("message"),
            response="",
        )

    def build_response_synthesizer(self, model_name: ModelName) -> StuffResponseSynthesizer:
        """Build the response synthesizer component.

        Args:
            model_name (ModelName): The model to use for inference.

        Returns:
            StuffResponseSynthesizer: The response synthesizer component.
        """
        lm_invoker = get_lm_invoker(model_name)
        prompt_builder = (
            self.catalog.no_op_agnostic if model_name.provider in UNIMODAL_PROVIDERS else self.catalog.no_op
        )
        response_synthesizer = StuffResponseSynthesizer.from_lm_components(prompt_builder, lm_invoker)
        return response_synthesizer
```
