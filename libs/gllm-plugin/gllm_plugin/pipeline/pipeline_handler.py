"""Pipeline handler for pipeline builder plugins.

This handler manages pipeline builder plugins and provides necessary services.

Authors:
    Samuel Lusandi (samuel.lusandi@gdplabs.id)
    Hermes Vincentius Gani (hermes.v.gani@gdplabs.id)
"""

from typing import Any, Type

from bosa_core import Plugin
from bosa_core.plugin.handler import PluginHandler
from gllm_core.utils import LoggerManager
from gllm_inference.catalog import PromptBuilderCatalog, LMRequestProcessorCatalog
from gllm_pipeline.pipeline.pipeline import Pipeline
from pydantic import BaseModel, ConfigDict

from gllm_plugin.config.app_config import AppConfig
from gllm_plugin.supported_models import ModelName


class ChatbotConfig(BaseModel):
    """Chatbot configuration class containing pipeline configs and metadata.
    
    Attributes:
        pipeline_type (str): Type of pipeline to use.
        pipeline_config (dict[str, Any]): Pipeline configuration dictionary.
        prompt_builder_catalogs (dict[str, PromptBuilderCatalog] | None): Mapping of prompt builder catalogs.
        lmrp_catalogs (dict[str, LMRequestProcessorCatalog] | None): Mapping of LM request processor catalogs.
    """

    pipeline_type: str
    pipeline_config: dict[str, Any]
    prompt_builder_catalogs: dict[str, PromptBuilderCatalog] | None
    lmrp_catalogs: dict[str, LMRequestProcessorCatalog] | None
    model_config = ConfigDict(arbitrary_types_allowed=True)


class PipelinePresetConfig(BaseModel):
    """Pipeline preset configuration class.
    
    Attributes:
        preset_id (str): Unique identifier for the pipeline preset.
        supported_models (list[str]): List of model names supported by this preset.
    """

    preset_id: str
    supported_models: list[str]


class ChatbotPresetMapping(BaseModel):
    """Chatbot preset mapping.
    
    Attributes:
        pipeline_type (str): Type of pipeline.
        chatbot_preset_map (dict[str, PipelinePresetConfig]): Mapping of chatbot IDs to their pipeline preset configurations.
    """

    pipeline_type: str
    chatbot_preset_map: dict[str, PipelinePresetConfig]


logger = LoggerManager().get_logger(__name__)


class PipelineHandler(PluginHandler):
    """Handler for pipeline builder plugins.

    This handler manages pipeline builder plugins and provides caching for built pipelines.

    Attributes:
        app_config (AppConfig): Application configuration.
        _activated_configs (dict[str, ChatbotPresetMapping]): Collection of chatbot preset mapping by pipeline types.
        _chatbot_configs (dict[str, ChatbotConfig]): Mapping of chatbot IDs to their configurations.
        _builders (dict[str, Plugin]): Mapping of chatbot IDs to their pipeline builder plugins.
        _pipeline_cache (dict[tuple[str, str], Pipeline]): Cache mapping (chatbot_id, model_name) to Pipeline instances.
    """
    app_config: AppConfig
    _activated_configs: dict[str, ChatbotPresetMapping] = {}
    _chatbot_configs: dict[str, ChatbotConfig] = {}
    _builders: dict[str, Plugin] = {}
    _pipeline_cache: dict[tuple[str, str], Pipeline] = {}

    def __init__(self, app_config: AppConfig):
        """Initialize the pipeline handler.

        Args:
            app_config: Application configuration.
        """
        self.app_config = app_config
        self._prepare_pipelines()

    @classmethod
    def create_injections(cls, instance: "PipelineHandler") -> dict[Type[Any], Any]:
        """Create injection mappings for pipeline builder plugins.

        Args:
            instance: The handler instance providing injections.

        Returns:
            Dictionary mapping service types to their instances.
        """
        return {AppConfig: instance.app_config}

    @classmethod
    def initialize_plugin(cls, instance: "PipelineHandler", plugin: Plugin) -> None:
        """Initialize plugin-specific resources.

        This method is called after plugin creation and service injection.
        For each pipeline builder plugin, we build pipelines for all supported models and cache them.

        Args:
            instance: The handler instance.
            plugin: The pipeline builder plugin instance.
        """
        pipeline_type = plugin.name

        if pipeline_type not in instance._activated_configs:
            return

        active_config = instance._activated_configs[pipeline_type]

        for chatbot_id, preset in active_config.chatbot_preset_map.items():
            if pipeline_type != instance._chatbot_configs[chatbot_id].pipeline_type:
                continue

            for model_name_str in preset.supported_models:
                model_name = ModelName.from_string(model_name_str)
                pipeline_config = instance._chatbot_configs[chatbot_id].pipeline_config.copy()
                pipeline_config["model_name"] = model_name
                plugin.prompt_builder_catalogs = instance._chatbot_configs[chatbot_id].prompt_builder_catalogs
                plugin.lmrp_catalogs = instance._chatbot_configs[chatbot_id].lmrp_catalogs
                pipeline = plugin.build(pipeline_config)
                instance._builders[chatbot_id] = plugin
                instance._pipeline_cache[(chatbot_id, str(model_name))] = pipeline

    def get_pipeline_builder(self, chatbot_id: str) -> Plugin:
        """Get a pipeline builder instance for the given chatbot.

        Args:
            chatbot_id (str): The chatbot ID.

        Returns:
            Plugin: The pipeline builder instance.

        Raises:
            ValueError: If the chatbot ID is invalid or the model name is not supported.
        """
        return self._builders[chatbot_id]

    def get_pipeline(self, chatbot_id: str, model_name: ModelName) -> Pipeline:
        """Get a pipeline instance for the given chatbot and model name.

        Args:
            chatbot_id (str): The chatbot ID.
            model_name (ModelName): The model to use for inference.

        Returns:
            Pipeline: The pipeline instance.

        Raises:
            ValueError: If the chatbot ID is invalid.
        """
        return self._pipeline_cache[(chatbot_id, str(model_name))]

    def get_pipeline_config(self, chatbot_id: str) -> dict[str, Any]:
        """Get the pipeline configuration by chatbot ID.

        Args:
            chatbot_id (str): The chatbot ID.

        Returns:
            dict[str, Any]: The pipeline configuration.

        Raises:
            ValueError: If the chatbot or pipeline is not found.
        """
        self._validate_pipeline(chatbot_id)
        return self._chatbot_configs[chatbot_id].pipeline_config

    def get_pipeline_type(self, chatbot_id: str) -> str:
        """Get the pipeline type for the given chatbot.

        Args:
            chatbot_id (str): The chatbot ID.
        """
        return self._chatbot_configs[chatbot_id].pipeline_type

    def get_use_docproc(self, chatbot_id: str) -> bool:
        """Get whether DocProc should be used for this chatbot.

        Args:
            chatbot_id (str): The chatbot ID.

        Returns:
            bool: Whether DocProc should be used.

        Raises:
            ValueError: If the chatbot or pipeline is not found.
        """
        self._validate_pipeline(chatbot_id)
        config = self._chatbot_configs[chatbot_id].pipeline_config
        return config["use_docproc"]

    def get_max_file_size(self, chatbot_id: str) -> int | None:
        """Get maximum file size for the given chatbot.

        Args:
            chatbot_id (str): The chatbot ID.

        Returns:
            int | None: The maximum file size if provided.

        Raises:
            ValueError: If the chatbot or pipeline is not found.
        Raises:
            ValueError: If the chatbot or pipeline is not found.
        """
        self._validate_pipeline(chatbot_id)
        config = self._chatbot_configs[chatbot_id].pipeline_config
        return config.get("max_file_size")

    def _prepare_pipelines(self) -> None:
        """Build pipeline configurations from the chatbots configuration."""

        pipeline_types: set[str] = set()
        chatbot_preset_map: dict[str, PipelinePresetConfig] = {}
        for chatbot_id, chatbot_info in self.app_config.chatbots.items():
            if not chatbot_info.pipeline:
                logger.warning(f"Pipeline config not found for chatbot `{chatbot_id}`")
                continue

            pipeline_info = chatbot_info.pipeline
            pipeline_type = pipeline_info["type"]

            chatbot_preset_map[chatbot_id] = PipelinePresetConfig(
                preset_id=pipeline_info["config"]["pipeline_preset_id"],
                supported_models=list(pipeline_info["config"]["supported_models"].keys()),
            )

            logger.info(f"Storing pipeline config for chatbot `{chatbot_id}`")
            self._chatbot_configs[chatbot_id] = ChatbotConfig(
                pipeline_type=pipeline_type,
                pipeline_config=pipeline_info["config"],
                prompt_builder_catalogs=pipeline_info["prompt_builder_catalogs"],
                lmrp_catalogs=pipeline_info["lmrp_catalogs"],
            )
            pipeline_types.add(pipeline_type)

        for pipeline_type in pipeline_types:
            self._activated_configs[pipeline_type] = ChatbotPresetMapping(
                pipeline_type=pipeline_type,
                chatbot_preset_map=chatbot_preset_map,
            )

    def _validate_pipeline(self, chatbot_id: str) -> None:
        """Validate the pipeline configuration exists.

        Args:
            chatbot_id (str): The chatbot ID.

        Raises:
            ValueError: If the chatbot or pipeline configuration is not found.
        """
        if chatbot_id not in self._chatbot_configs:
            raise ValueError(f"Pipeline configuration for chatbot `{chatbot_id}` not found")
            