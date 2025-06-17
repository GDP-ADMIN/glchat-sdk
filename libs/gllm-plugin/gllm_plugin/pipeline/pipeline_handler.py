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
from gllm_inference.catalog import LMRequestProcessorCatalog, PromptBuilderCatalog
from gllm_pipeline.pipeline.pipeline import Pipeline
from pydantic import BaseModel, ConfigDict

from gllm_plugin.config.app_config import AppConfig
from gllm_plugin.storage.base_chat_history_storage import BaseChatHistoryStorage
from gllm_plugin.supported_models import MODEL_KEY_MAP, ModelName


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
        chatbot_preset_map (dict[str, PipelinePresetConfig]):
            Mapping of chatbot IDs to their pipeline preset configurations.
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
        _plugins (dict[str, Plugin]): Mapping of pipeline types to their plugins.
        _pipeline_cache (dict[tuple[str, str], Pipeline]): Cache mapping (chatbot_id, model_name) to Pipeline instances.
        _chatbot_pipeline_keys (dict[str, set[tuple[str, str]]]): Mapping of chatbot IDs to their pipeline keys.
    """

    app_config: AppConfig
    _activated_configs: dict[str, ChatbotPresetMapping] = {}
    _chatbot_configs: dict[str, ChatbotConfig] = {}
    _builders: dict[str, Plugin] = {}
    _plugins: dict[str, Plugin] = {}
    _pipeline_cache: dict[tuple[str, str], Pipeline] = {}
    _chatbot_pipeline_keys: dict[str, set[tuple[str, str]]] = {}

    def __init__(self, app_config: AppConfig, chat_history_storage: BaseChatHistoryStorage):
        """Initialize the pipeline handler.

        Args:
            app_config (AppConfig): Application configuration.
            chat_history_storage (BaseChatHistoryStorage): Chat history storage.
        """
        self.app_config = app_config
        self.chat_history_storage = chat_history_storage
        self._prepare_pipelines()

    @classmethod
    def create_injections(cls, instance: "PipelineHandler") -> dict[Type[Any], Any]:
        """Create injection mappings for pipeline builder plugins.

        Args:
            instance (PipelineHandler): The handler instance providing injections.

        Returns:
            dict[Type[Any], Any]: Dictionary mapping service types to their instances.
        """
        return {
            AppConfig: instance.app_config,
            BaseChatHistoryStorage: instance.chat_history_storage,
        }

    @classmethod
    def initialize_plugin(cls, instance: "PipelineHandler", plugin: Plugin) -> None:
        """Initialize plugin-specific resources.

        This method is called after plugin creation and service injection.
        For each pipeline builder plugin, we build pipelines for all supported models and cache them.

        Args:
            instance (PipelineHandler): The handler instance.
            plugin (Plugin): The pipeline builder plugin instance.
        """
        pass

    @classmethod
    async def ainitialize_plugin(cls, instance: "PipelineHandler", plugin: Plugin) -> None:
        """Initialize plugin-specific resources.

        This method is called after plugin creation and service injection.
        For each pipeline builder plugin, we build pipelines for all supported models and cache them.

        Args:
            instance (PipelineHandler): The handler instance.
            plugin (Plugin): The pipeline builder plugin instance.
        """
        pipeline_type = plugin.name

        if pipeline_type not in instance._activated_configs:
            return

        active_config = instance._activated_configs[pipeline_type]
        instance._plugins[pipeline_type] = plugin

        for chatbot_id, preset in active_config.chatbot_preset_map.items():
            try:
                if pipeline_type != instance._chatbot_configs[chatbot_id].pipeline_type:
                    continue

                await cls._build_plugin(instance, chatbot_id, preset.supported_models, plugin)
            except Exception as e:
                logger.error(f"Error initializing plugin for chatbot `{chatbot_id}`: {e}")
                pass

    @classmethod
    async def acleanup_plugins(cls, instance: "PipelineHandler") -> None:
        """Cleanup all plugins.

        Args:
            instance (PipelineHandler): The handler instance.
        """
        for plugin in instance._plugins.values():
            await plugin.cleanup()

    @classmethod
    async def _build_plugin(
        cls, instance: "PipelineHandler", chatbot_id: str, supported_models: list[str], plugin: Plugin
    ) -> None:
        """Build a plugin for the given chatbot.

        Args:
            instance (PipelineHandler): The handler instance.
            chatbot_id (str): The chatbot ID.
            supported_models (list[str]): List of supported models.
            plugin (Plugin): The pipeline builder plugin instance.
        """
        plugin.prompt_builder_catalogs = instance._chatbot_configs[chatbot_id].prompt_builder_catalogs
        plugin.lmrp_catalogs = instance._chatbot_configs[chatbot_id].lmrp_catalogs
        instance._builders[chatbot_id] = plugin

        for model_name_str in supported_models:
            model_name = ModelName.from_string(model_name_str)
            pipeline_config = instance._chatbot_configs[chatbot_id].pipeline_config.copy()
            pipeline_config["model_name"] = model_name
            provider = model_name.provider
            api_key = MODEL_KEY_MAP.get(provider)
            if api_key:
                pipeline_config["api_key"] = api_key

            pipeline = await plugin.build(pipeline_config)
            pipeline_key = (chatbot_id, str(model_name))
            instance._chatbot_pipeline_keys.setdefault(chatbot_id, set()).add(pipeline_key)
            instance._pipeline_cache[pipeline_key] = pipeline

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
        """
        self._validate_pipeline(chatbot_id)
        config = self._chatbot_configs[chatbot_id].pipeline_config
        return config.get("max_file_size")

    async def create_chatbot(self, app_config: AppConfig, chatbot_id: str) -> None:
        """Create a new chatbot.

        Args:
            app_config (AppConfig): The application configuration.
            chatbot_id (str): The ID of the chatbot.
        """
        chatbot_info = app_config.chatbots.get(chatbot_id)

        if not chatbot_info or not chatbot_info.pipeline:
            logger.warning(f"Pipeline config not found for chatbot `{chatbot_id}`")
            return

        pipeline_info = chatbot_info.pipeline
        pipeline_type = pipeline_info["type"]
        plugin = self._plugins[pipeline_type]

        logger.info(f"Storing pipeline config for chatbot `{chatbot_id}`")
        self._chatbot_configs[chatbot_id] = ChatbotConfig(
            pipeline_type=pipeline_type,
            pipeline_config=pipeline_info["config"],
            prompt_builder_catalogs=pipeline_info["prompt_builder_catalogs"],
            lmrp_catalogs=pipeline_info["lmrp_catalogs"],
        )

        supported_models = list(pipeline_info["config"]["supported_models"].keys())
        await __class__._build_plugin(self, chatbot_id, supported_models, plugin)

    async def delete_chatbot(self, chatbot_id: str) -> None:
        """Delete a chatbot.

        Args:
            chatbot_id (str): The ID of the chatbot.
        """
        for pipeline_keys in self._chatbot_pipeline_keys.get(chatbot_id, set()):
            for pipeline_key in pipeline_keys:
                self._pipeline_cache.pop(pipeline_key, None)

        self._chatbot_pipeline_keys.pop(chatbot_id, None)
        self._chatbot_configs.pop(chatbot_id, None)
        self._builders.pop(chatbot_id, None)

    async def update_chatbots(self, app_config: AppConfig, chatbot_ids: list[str]) -> None:
        """Update the chatbots.

        Args:
            app_config (AppConfig): The application configuration.
            chatbot_ids (list[str]): The updated chatbot IDs.
        """
        for chatbot_id in chatbot_ids:
            try:
                chatbot_info = app_config.chatbots.get(chatbot_id)
                if not chatbot_info or not chatbot_info.pipeline:
                    logger.warning(f"Pipeline config not found for chatbot `{chatbot_id}`")
                    continue

                pipeline_info = chatbot_info.pipeline
                pipeline_type = pipeline_info["type"]

                supported_models = list(pipeline_info["config"]["supported_models"].keys())

                logger.info(f"Storing pipeline config for chatbot `{chatbot_id}`")
                self._chatbot_configs.pop(chatbot_id, None)
                self._chatbot_configs[chatbot_id] = ChatbotConfig(
                    pipeline_type=pipeline_type,
                    pipeline_config=pipeline_info["config"],
                    prompt_builder_catalogs=pipeline_info["prompt_builder_catalogs"],
                    lmrp_catalogs=pipeline_info["lmrp_catalogs"],
                )

                new_pipeline_keys = set()
                for model_name_str in supported_models:
                    model_name = ModelName.from_string(model_name_str)
                    new_pipeline_key = (chatbot_id, str(model_name))
                    new_pipeline_keys.add(new_pipeline_key)

                for pipeline_key in self._chatbot_pipeline_keys.get(chatbot_id, set()):
                    if pipeline_key not in new_pipeline_keys:
                        self._pipeline_cache.pop(pipeline_key, None)

                self._chatbot_pipeline_keys[chatbot_id] = set()

                plugin = self._builders[chatbot_id]

                await __class__._build_plugin(self, chatbot_id, supported_models, plugin)
            except Exception as e:
                logger.error(f"Error initializing plugin for chatbot `{chatbot_id}`: {e}")
                pass

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
