"""Unit tests for PipelineHandler class."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from bosa_core import Plugin
from gllm_inference.catalog import LMRequestProcessorCatalog, PromptBuilderCatalog
from gllm_pipeline.pipeline.pipeline import Pipeline

from glchat_plugin.config.app_config import AppConfig
from glchat_plugin.pipeline.pipeline_handler import (
    ChatbotConfig,
    ChatbotPresetMapping,
    PipelineHandler,
    PipelinePresetConfig,
)
from glchat_plugin.storage.base_chat_history_storage import BaseChatHistoryStorage


@pytest.fixture
def mock_app_config() -> Mock:
    """Create a mock AppConfig instance."""
    config = Mock(spec=AppConfig)
    config.chatbots = {
        "chatbot1": Mock(
            pipeline={
                "type": "pipeline_type1",
                "config": {
                    "pipeline_preset_id": "preset1",
                    "use_docproc": True,
                    "max_file_size": 1024,
                    "supported_models": {
                        "model1": {"name": "gpt-3", "model_kwargs": {}, "model_env_kwargs": {}},
                        "model2": {
                            "name": "gpt-4",
                            "model_kwargs": {},
                            "model_env_kwargs": {"credentials": "test_key"},
                        },
                    },
                },
                "prompt_builder_catalogs": {"catalog1": Mock(spec=PromptBuilderCatalog)},
                "lmrp_catalogs": {"lmrp1": Mock(spec=LMRequestProcessorCatalog)},
            }
        ),
        "chatbot2": Mock(
            pipeline={
                "type": "pipeline_type2",
                "config": {
                    "pipeline_preset_id": "preset2",
                    "use_docproc": False,
                    "supported_models": {"model3": {"name": "claude", "model_kwargs": {}, "model_env_kwargs": {}}},
                },
                "prompt_builder_catalogs": None,
                "lmrp_catalogs": None,
            }
        ),
        "chatbot_no_pipeline": Mock(pipeline=None),
    }
    return config


@pytest.fixture
def mock_chat_history_storage() -> Mock:
    """Create a mock BaseChatHistoryStorage instance."""
    return Mock(spec=BaseChatHistoryStorage)


@pytest.fixture
def pipeline_handler(mock_app_config: Mock, mock_chat_history_storage: Mock) -> PipelineHandler:
    """Create a PipelineHandler instance with mocked dependencies."""
    return PipelineHandler(mock_app_config, mock_chat_history_storage)


@pytest.fixture
def empty_pipeline_handler(mock_chat_history_storage: Mock) -> PipelineHandler:
    """Create a PipelineHandler instance with empty configuration."""
    empty_config = Mock(spec=AppConfig)
    empty_config.chatbots = {}
    pipeline_handler = PipelineHandler(empty_config, mock_chat_history_storage)
    pipeline_handler._pipeline_cache = {}
    pipeline_handler._activated_configs = {}
    pipeline_handler._chatbot_configs = {}
    pipeline_handler._builders = {}
    pipeline_handler._plugins = {}
    pipeline_handler._chatbot_pipeline_keys = {}
    return pipeline_handler


@pytest.fixture
def mock_plugin() -> Mock:
    """Create a mock Plugin instance."""
    plugin = Mock(spec=Plugin)
    plugin.name = "pipeline_type1"
    plugin.build = AsyncMock(return_value=Mock(spec=Pipeline))
    plugin.cleanup = AsyncMock()
    return plugin


def test_init_prepares_pipelines(mock_app_config: Mock, mock_chat_history_storage: Mock):
    """
    Condition:
    - Valid app_config with multiple chatbots having pipeline configurations
    - Valid chat_history_storage instance

    Expected:
    - Handler initializes with correct attributes
    - _prepare_pipelines is called and populates internal structures
    """
    handler = PipelineHandler(mock_app_config, mock_chat_history_storage)

    assert handler.app_config == mock_app_config
    assert handler.chat_history_storage == mock_chat_history_storage
    assert len(handler._chatbot_configs) == 2
    assert "chatbot1" in handler._chatbot_configs
    assert "chatbot2" in handler._chatbot_configs
    assert len(handler._activated_configs) == 2


def test_init_handles_chatbot_without_pipeline(mock_app_config: Mock, mock_chat_history_storage: Mock):
    """
    Condition:
    - App config contains chatbot without pipeline configuration

    Expected:
    - Handler initializes successfully
    - Chatbot without pipeline is not included in _chatbot_configs
    """
    handler = PipelineHandler(mock_app_config, mock_chat_history_storage)

    assert "chatbot_no_pipeline" not in handler._chatbot_configs


def test_create_injections(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Valid PipelineHandler instance

    Expected:
    - Returns correct injection mappings with AppConfig and BaseChatHistoryStorage
    """
    injections = PipelineHandler.create_injections(pipeline_handler)

    assert AppConfig in injections
    assert BaseChatHistoryStorage in injections
    assert injections[AppConfig] == pipeline_handler.app_config
    assert injections[BaseChatHistoryStorage] == pipeline_handler.chat_history_storage


def test_initialize_plugin(pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Valid plugin instance passed to initialize_plugin

    Expected:
    - Method completes without error (no-op implementation)
    """
    # Should not raise any exceptions
    PipelineHandler.initialize_plugin(pipeline_handler, mock_plugin)


@pytest.mark.asyncio
async def test_ainitialize_plugin_success(pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Valid plugin with matching pipeline type in activated configs
    - Plugin build succeeds for all models

    Expected:
    - Plugin is stored in _plugins
    - Pipelines are built and cached for all supported models
    """
    pipeline_handler._activated_configs["pipeline_type1"] = ChatbotPresetMapping(
        pipeline_type="pipeline_type1",
        chatbot_preset_map={
            "chatbot1": PipelinePresetConfig(
                preset_id="preset1",
                supported_models=[
                    {"name": "gpt-3", "model_kwargs": {}, "model_env_kwargs": {}},
                    {"name": "gpt-4", "model_kwargs": {}, "model_env_kwargs": {"credentials": "test_key"}},
                    {"model_id": "GPT 3", "name": "gpt-3", "model_kwargs": {}, "model_env_kwargs": {}},
                ],
            )
        },
    )

    await PipelineHandler.ainitialize_plugin(pipeline_handler, mock_plugin)

    assert "pipeline_type1" in pipeline_handler._plugins
    assert pipeline_handler._plugins["pipeline_type1"] == mock_plugin
    assert ("chatbot1", "gpt-3") in pipeline_handler._pipeline_cache
    assert ("chatbot1", "gpt-4") in pipeline_handler._pipeline_cache
    assert ("chatbot1", "GPT 3") in pipeline_handler._pipeline_cache
    assert mock_plugin.build.call_count == 3


@pytest.mark.asyncio
async def test_ainitialize_plugin_no_matching_config(pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Plugin type not in activated configs

    Expected:
    - Method stores plugin in _plugins but returns early without building pipelines
    """
    mock_plugin.name = "unknown_type"

    await PipelineHandler.ainitialize_plugin(pipeline_handler, mock_plugin)

    # The plugin is stored regardless of whether it has a matching config
    assert "unknown_type" in pipeline_handler._plugins
    # But no pipelines are built
    assert mock_plugin.build.call_count == 0


@pytest.mark.asyncio
async def test_ainitialize_plugin_handles_build_error(empty_pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Plugin build raises exception for one of the models

    Expected:
    - Error is logged but doesn't stop processing other models
    - Successfully built pipelines are still cached
    """
    # Setup handler with specific configs
    empty_pipeline_handler._chatbot_configs["chatbot1"] = ChatbotConfig(
        pipeline_type="pipeline_type1",
        pipeline_config={"test": "config"},
        prompt_builder_catalogs=None,
        lmrp_catalogs=None,
    )

    empty_pipeline_handler._activated_configs["pipeline_type1"] = ChatbotPresetMapping(
        pipeline_type="pipeline_type1",
        chatbot_preset_map={
            "chatbot1": PipelinePresetConfig(
                preset_id="preset1",
                supported_models=[
                    {"name": "gpt-3", "model_kwargs": {}, "model_env_kwargs": {}},
                    {"name": "gpt-4", "model_kwargs": {}, "model_env_kwargs": {}},
                ],
            )
        },
    )

    # First call succeeds, second fails
    mock_plugin.build.side_effect = [Mock(spec=Pipeline), Exception("Build failed")]

    with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        await PipelineHandler.ainitialize_plugin(empty_pipeline_handler, mock_plugin)

        assert mock_logger.warning.called
        assert ("chatbot1", "gpt-3") in empty_pipeline_handler._pipeline_cache
        assert ("chatbot1", "gpt-4") not in empty_pipeline_handler._pipeline_cache


@pytest.mark.asyncio
async def test_acleanup_plugins_success(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Multiple plugins exist in _plugins
    - All cleanup operations succeed

    Expected:
    - cleanup() is called on all plugins
    """
    plugin1 = Mock(spec=Plugin)
    plugin1.cleanup = AsyncMock()
    plugin2 = Mock(spec=Plugin)
    plugin2.cleanup = AsyncMock()

    pipeline_handler._plugins = {"type1": plugin1, "type2": plugin2}

    await PipelineHandler.acleanup_plugins(pipeline_handler)

    plugin1.cleanup.assert_called_once()
    plugin2.cleanup.assert_called_once()


@pytest.mark.asyncio
async def test_acleanup_plugins_handles_errors(pipeline_handler: PipelineHandler):
    """
    Condition:
    - One plugin cleanup raises exception

    Expected:
    - Error is logged but doesn't stop cleanup of other plugins
    """
    plugin1 = Mock(spec=Plugin)
    plugin1.name = "plugin1"
    plugin1.cleanup = AsyncMock(side_effect=Exception("Cleanup failed"))
    plugin2 = Mock(spec=Plugin)
    plugin2.cleanup = AsyncMock()

    pipeline_handler._plugins = {"type1": plugin1, "type2": plugin2}

    with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        await PipelineHandler.acleanup_plugins(pipeline_handler)

        assert mock_logger.warning.called
        plugin2.cleanup.assert_called_once()


@pytest.mark.asyncio
async def test_build_plugin_with_model_env_credentials(pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Model has credentials in model_env_kwargs

    Expected:
    - Credentials are copied to api_key for backward compatibility
    """
    supported_models = [{"name": "gpt-4", "model_kwargs": {}, "model_env_kwargs": {"credentials": "test_key"}}]

    await PipelineHandler._build_plugin(pipeline_handler, "chatbot1", supported_models, mock_plugin)

    # Check that build was called with api_key set
    build_call_args = mock_plugin.build.call_args[0][0]
    assert build_call_args["api_key"] == "test_key"


@pytest.mark.asyncio
async def test_build_plugin_without_model_name(pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Model in supported_models list has no name

    Expected:
    - Model is skipped without error
    """
    supported_models = [{"model_kwargs": {}, "model_env_kwargs": {}}]  # No name field

    await PipelineHandler._build_plugin(pipeline_handler, "chatbot1", supported_models, mock_plugin)

    assert mock_plugin.build.call_count == 0


@pytest.mark.asyncio
async def test_aget_pipeline_builder_success(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Valid chatbot_id with existing builder

    Expected:
    - Returns correct plugin builder
    """
    mock_builder = Mock(spec=Plugin)
    pipeline_handler._builders["chatbot1"] = mock_builder

    result = await pipeline_handler.aget_pipeline_builder("chatbot1")

    assert result == mock_builder


@pytest.mark.asyncio
async def test_aget_pipeline_builder_not_found(pipeline_handler: PipelineHandler):
    """
    Condition:
    - chatbot_id not in _builders and rebuild fails

    Expected:
    - Raises ValueError with descriptive message
    """
    with pytest.raises(
        ValueError, match="Pipeline builder for chatbot `nonexistent` not found and could not be rebuilt"
    ):
        await pipeline_handler.aget_pipeline_builder("nonexistent")


@pytest.mark.asyncio
async def test_aget_pipeline_success(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Valid chatbot_id and model_name with cached pipeline

    Expected:
    - Returns correct pipeline instance
    """
    mock_pipeline = Mock(spec=Pipeline)
    pipeline_handler._pipeline_cache[("chatbot1", "gpt-3")] = mock_pipeline

    result = await pipeline_handler.aget_pipeline("chatbot1", "gpt-3")

    assert result == mock_pipeline


@pytest.mark.asyncio
async def test_aget_pipeline_not_found(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Pipeline key not in cache and rebuild fails

    Expected:
    - Raises ValueError with descriptive message
    """
    with pytest.raises(
        ValueError, match="Pipeline for chatbot `chatbot1` model `nonexistent_model` not found and could not be rebuilt"
    ):
        await pipeline_handler.aget_pipeline("chatbot1", "nonexistent_model")


def test_get_pipeline_config_success(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Valid chatbot_id with existing configuration

    Expected:
    - Returns correct pipeline configuration
    """
    result = pipeline_handler.get_pipeline_config("chatbot1")

    expected_config = pipeline_handler._chatbot_configs["chatbot1"].pipeline_config
    assert result == expected_config


def test_get_pipeline_config_not_found(pipeline_handler: PipelineHandler):
    """
    Condition:
    - chatbot_id not in _chatbot_configs

    Expected:
    - Raises ValueError
    """
    with pytest.raises(ValueError, match="Pipeline configuration for chatbot `nonexistent` not found"):
        pipeline_handler.get_pipeline_config("nonexistent")


def test_get_pipeline_type_success(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Valid chatbot_id with existing configuration

    Expected:
    - Returns correct pipeline type
    """
    result = pipeline_handler.get_pipeline_type("chatbot1")

    assert result == "pipeline_type1"


def test_get_pipeline_type_not_found(pipeline_handler: PipelineHandler):
    """
    Condition:
    - chatbot_id not in _chatbot_configs

    Expected:
    - Raises KeyError (direct dictionary access)
    """
    with pytest.raises(KeyError):
        pipeline_handler.get_pipeline_type("nonexistent")


def test_get_use_docproc_true(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Valid chatbot_id with use_docproc set to True

    Expected:
    - Returns True
    """
    result = pipeline_handler.get_use_docproc("chatbot1")

    assert result is True


def test_get_use_docproc_false(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Valid chatbot_id with use_docproc set to False

    Expected:
    - Returns False
    """
    result = pipeline_handler.get_use_docproc("chatbot2")

    assert result is False


def test_get_use_docproc_not_found(pipeline_handler: PipelineHandler):
    """
    Condition:
    - chatbot_id not in _chatbot_configs

    Expected:
    - Raises ValueError
    """
    with pytest.raises(ValueError):
        pipeline_handler.get_use_docproc("nonexistent")


def test_get_max_file_size_with_value(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Valid chatbot_id with max_file_size configured

    Expected:
    - Returns configured max_file_size value
    """
    result = pipeline_handler.get_max_file_size("chatbot1")

    assert result == 1024


def test_get_max_file_size_not_configured(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Valid chatbot_id without max_file_size in config

    Expected:
    - Returns None
    """
    result = pipeline_handler.get_max_file_size("chatbot2")

    assert result is None


def test_get_max_file_size_not_found(pipeline_handler: PipelineHandler):
    """
    Condition:
    - chatbot_id not in _chatbot_configs

    Expected:
    - Raises ValueError
    """
    with pytest.raises(ValueError):
        pipeline_handler.get_max_file_size("nonexistent")


@pytest.mark.asyncio
async def test_create_chatbot_success(pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Valid chatbot configuration in app_config
    - Matching plugin exists

    Expected:
    - Chatbot config is stored
    - Pipelines are built for all supported models
    """
    pipeline_handler._plugins["new_pipeline_type"] = mock_plugin
    mock_plugin.name = "new_pipeline_type"

    new_app_config = Mock(spec=AppConfig)
    new_app_config.chatbots = {
        "new_chatbot": Mock(
            pipeline={
                "type": "new_pipeline_type",
                "config": {
                    "supported_models": {"model1": {"name": "new_model", "model_kwargs": {}, "model_env_kwargs": {}}}
                },
                "prompt_builder_catalogs": None,
                "lmrp_catalogs": None,
            }
        )
    }

    await pipeline_handler.create_chatbot(new_app_config, "new_chatbot")

    assert "new_chatbot" in pipeline_handler._chatbot_configs
    assert mock_plugin.build.called


@pytest.mark.asyncio
async def test_create_chatbot_no_pipeline_config(empty_pipeline_handler: PipelineHandler):
    """
    Condition:
    - Chatbot has no pipeline configuration

    Expected:
    - Method logs warning and returns early
    """
    new_app_config = Mock(spec=AppConfig)
    new_app_config.chatbots = {"new_chatbot": Mock(pipeline=None)}

    with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        await empty_pipeline_handler.create_chatbot(new_app_config, "new_chatbot")

        assert mock_logger.warning.called
        assert "new_chatbot" not in empty_pipeline_handler._chatbot_configs


@pytest.mark.asyncio
async def test_create_chatbot_no_matching_plugin(empty_pipeline_handler: PipelineHandler):
    """
    Condition:
    - Pipeline type has no matching plugin

    Expected:
    - Method logs warning and returns early
    """
    # Use empty_pipeline_handler to ensure a clean state
    # Note: empty_pipeline_handler has an empty _plugins dictionary by default

    new_app_config = Mock(spec=AppConfig)
    new_app_config.chatbots = {
        "new_chatbot": Mock(
            pipeline={"type": "unknown_type", "config": {}, "prompt_builder_catalogs": None, "lmrp_catalogs": None}
        )
    }

    with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        await empty_pipeline_handler.create_chatbot(new_app_config, "new_chatbot")

        # Verify warning was logged
        mock_logger.warning.assert_called_once_with("Pipeline plugin not found for chatbot `new_chatbot`")
        # Verify the chatbot wasn't added to the configs
        assert "new_chatbot" not in empty_pipeline_handler._chatbot_configs


@pytest.mark.asyncio
async def test_delete_chatbot_success(empty_pipeline_handler: PipelineHandler):
    """
    Condition:
    - Chatbot exists with cached pipelines and configurations

    Expected:
    - All related data is removed from internal structures
    """
    # Setup test data
    empty_pipeline_handler._pipeline_cache[("test_chatbot", "model1")] = Mock(spec=Pipeline)
    empty_pipeline_handler._pipeline_cache[("test_chatbot", "model2")] = Mock(spec=Pipeline)
    empty_pipeline_handler._chatbot_pipeline_keys["test_chatbot"] = {
        ("test_chatbot", "model1"),
        ("test_chatbot", "model2"),
    }
    empty_pipeline_handler._chatbot_configs["test_chatbot"] = Mock(spec=ChatbotConfig)
    empty_pipeline_handler._builders["test_chatbot"] = Mock(spec=Plugin)

    await empty_pipeline_handler.delete_chatbot("test_chatbot")

    assert ("test_chatbot", "model1") not in empty_pipeline_handler._pipeline_cache
    assert ("test_chatbot", "model2") not in empty_pipeline_handler._pipeline_cache
    assert "test_chatbot" not in empty_pipeline_handler._chatbot_pipeline_keys
    assert "test_chatbot" not in empty_pipeline_handler._chatbot_configs
    assert "test_chatbot" not in empty_pipeline_handler._builders


@pytest.mark.asyncio
async def test_delete_chatbot_not_found(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Chatbot doesn't exist

    Expected:
    - Method completes without error (graceful handling)
    """
    # Should not raise exception
    await pipeline_handler.delete_chatbot("nonexistent")


@pytest.mark.asyncio
async def test_update_chatbots_success(pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Valid chatbot configurations to update
    - Matching plugins exist

    Expected:
    - Old pipelines are removed
    - New configurations are stored
    - New pipelines are built
    """
    pipeline_handler._plugins["pipeline_type1"] = mock_plugin
    mock_plugin.name = "pipeline_type1"

    # Add existing data to be updated
    old_pipeline_key = ("chatbot1", "old_model")
    model1_pipeline_key = ("chatbot1", "model1")
    pipeline_handler._pipeline_cache[old_pipeline_key] = Mock(spec=Pipeline)
    pipeline_handler._pipeline_cache[model1_pipeline_key] = Mock(spec=Pipeline)
    pipeline_handler._chatbot_pipeline_keys["chatbot1"] = {old_pipeline_key, model1_pipeline_key}

    updated_app_config = Mock(spec=AppConfig)
    updated_app_config.chatbots = {
        "chatbot1": Mock(
            pipeline={
                "type": "pipeline_type1",
                "config": {
                    "supported_models": {
                        "model1": {"name": "model1", "model_kwargs": {}, "model_env_kwargs": {}},
                        "model2": {"name": "model2", "model_kwargs": {}, "model_env_kwargs": {}},
                    }
                },
                "prompt_builder_catalogs": None,
                "lmrp_catalogs": None,
            }
        )
    }

    await pipeline_handler.update_chatbots(updated_app_config, ["chatbot1"])

    assert old_pipeline_key not in pipeline_handler._pipeline_cache
    assert ("chatbot1", "model1") in pipeline_handler._chatbot_pipeline_keys["chatbot1"]
    assert ("chatbot1", "model2") in pipeline_handler._chatbot_pipeline_keys["chatbot1"]
    assert mock_plugin.build.called


@pytest.mark.asyncio
async def test_update_chatbots_handles_errors(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Error occurs during update of one chatbot

    Expected:
    - Error is logged but doesn't stop processing other chatbots
    """
    updated_app_config = Mock(spec=AppConfig)
    updated_app_config.chatbots = {
        "chatbot1": Mock(pipeline=None),  # Will cause warning
        "chatbot2": Mock(
            pipeline={
                "type": "pipeline_type2",
                "config": {"supported_models": {}},
                "prompt_builder_catalogs": None,
                "lmrp_catalogs": None,
            }
        ),
    }

    with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        await pipeline_handler.update_chatbots(updated_app_config, ["chatbot1", "chatbot2"])

        assert mock_logger.warning.called


def test_validate_pipeline_valid_chatbot(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Valid chatbot_id exists in _chatbot_configs

    Expected:
    - Method completes without error
    """
    # Should not raise exception
    pipeline_handler._validate_pipeline("chatbot1")


def test_validate_pipeline_invalid_chatbot(pipeline_handler: PipelineHandler):
    """
    Condition:
    - chatbot_id not in _chatbot_configs

    Expected:
    - Raises ValueError with descriptive message
    """
    with pytest.raises(ValueError, match="Pipeline configuration for chatbot `nonexistent` not found"):
        pipeline_handler._validate_pipeline("nonexistent")


@pytest.mark.parametrize(
    "model_name,expected_key",
    [
        ("gpt-3", ("chatbot1", "gpt-3")),
        (123, ("chatbot1", "123")),  # Test non-string model names
        (None, ("chatbot1", "None")),
    ],
)
@pytest.mark.asyncio
async def test_aget_pipeline_handles_different_model_types(
    pipeline_handler: PipelineHandler, model_name: Any, expected_key: tuple[str, str]
):
    """
    Condition:
    - Various types of model_name values

    Expected:
    - Model name is converted to string for cache key
    """
    mock_pipeline = Mock(spec=Pipeline)
    pipeline_handler._pipeline_cache[expected_key] = mock_pipeline

    result = await pipeline_handler.aget_pipeline("chatbot1", model_name)

    assert result == mock_pipeline


@pytest.mark.asyncio
async def test_delete_chatbot_with_pipeline_keys_typo(empty_pipeline_handler: PipelineHandler):
    """
    Condition:
    - _chatbot_pipeline_keys contains incorrect structure (typo in code)

    Expected:
    - Method handles the error gracefully
    """
    # The original code has a bug where it iterates over pipeline_keys twice
    # Let's test the correct behavior
    empty_pipeline_handler._pipeline_cache[("test_chatbot", "model1")] = Mock(spec=Pipeline)
    empty_pipeline_handler._chatbot_pipeline_keys["test_chatbot"] = {("test_chatbot", "model1")}

    await empty_pipeline_handler.delete_chatbot("test_chatbot")

    assert ("test_chatbot", "model1") not in empty_pipeline_handler._pipeline_cache
    assert "test_chatbot" not in empty_pipeline_handler._chatbot_pipeline_keys


@pytest.mark.asyncio
async def test_async_rebuild_plugin_success(empty_pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Valid chatbot_id with existing configuration
    - Plugin exists for the pipeline type
    - Supported models are configured

    Expected:
    - _build_plugin is called with correct parameters
    - Plugin is successfully rebuilt
    """
    # Setup test data
    chatbot_id = "test_chatbot"
    pipeline_type = "pipeline_type1"

    empty_pipeline_handler._chatbot_configs[chatbot_id] = ChatbotConfig(
        pipeline_type=pipeline_type,
        pipeline_config={
            "supported_models": {
                "model1": {"name": "model1", "model_kwargs": {}, "model_env_kwargs": {}},
                "model2": {"name": "model2", "model_kwargs": {}, "model_env_kwargs": {}},
            }
        },
        prompt_builder_catalogs=None,
        lmrp_catalogs=None,
    )

    empty_pipeline_handler._plugins[pipeline_type] = mock_plugin

    # Mock the _build_plugin method
    with patch.object(PipelineHandler, "_build_plugin", new_callable=AsyncMock) as mock_build_plugin:
        await empty_pipeline_handler._async_rebuild_plugin(chatbot_id)

        # Verify _build_plugin was called with correct parameters
        mock_build_plugin.assert_called_once()
        call_args = mock_build_plugin.call_args[0]
        assert call_args[0] is empty_pipeline_handler  # self
        assert call_args[1] == chatbot_id
        assert len(call_args[2]) == 2  # supported_models list
        assert call_args[3] == mock_plugin


@pytest.mark.asyncio
async def test_async_rebuild_plugin_chatbot_not_found(empty_pipeline_handler: PipelineHandler):
    """
    Condition:
    - chatbot_id not in _chatbot_configs

    Expected:
    - Method logs warning and returns early
    - _build_plugin is not called
    """
    with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        with patch.object(PipelineHandler, "_build_plugin", new_callable=AsyncMock) as mock_build_plugin:
            await empty_pipeline_handler._async_rebuild_plugin("nonexistent_chatbot")

            mock_logger.warning.assert_called_once()
            mock_build_plugin.assert_not_called()


@pytest.mark.asyncio
async def test_async_rebuild_plugin_plugin_not_found(empty_pipeline_handler: PipelineHandler):
    """
    Condition:
    - Valid chatbot_id with existing configuration
    - Plugin does not exist for the pipeline type

    Expected:
    - Method logs warning and returns early
    - _build_plugin is not called
    """
    # Setup test data
    chatbot_id = "test_chatbot"
    pipeline_type = "unknown_pipeline_type"

    empty_pipeline_handler._chatbot_configs[chatbot_id] = ChatbotConfig(
        pipeline_type=pipeline_type, pipeline_config={}, prompt_builder_catalogs=None, lmrp_catalogs=None
    )

    with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        with patch.object(PipelineHandler, "_build_plugin", new_callable=AsyncMock) as mock_build_plugin:
            await empty_pipeline_handler._async_rebuild_plugin(chatbot_id)

            mock_logger.warning.assert_called_once()
            mock_build_plugin.assert_not_called()


@pytest.mark.asyncio
async def test_async_rebuild_plugin_no_supported_models(empty_pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Valid chatbot_id with existing configuration
    - Plugin exists for the pipeline type
    - No supported models in configuration

    Expected:
    - Method logs warning and returns early
    - _build_plugin is not called
    """
    # Setup test data
    chatbot_id = "test_chatbot"
    pipeline_type = "pipeline_type1"

    empty_pipeline_handler._chatbot_configs[chatbot_id] = ChatbotConfig(
        pipeline_type=pipeline_type,
        pipeline_config={"supported_models": {}},  # Empty supported_models
        prompt_builder_catalogs=None,
        lmrp_catalogs=None,
    )

    empty_pipeline_handler._plugins[pipeline_type] = mock_plugin

    with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        with patch.object(PipelineHandler, "_build_plugin", new_callable=AsyncMock) as mock_build_plugin:
            await empty_pipeline_handler._async_rebuild_plugin(chatbot_id)

            mock_logger.warning.assert_called_once()
            mock_build_plugin.assert_not_called()


@pytest.mark.asyncio
async def test_async_rebuild_plugin_handles_exception(empty_pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Valid setup but _build_plugin raises an exception

    Expected:
    - Exception is caught and logged
    - Method completes without raising exception
    """
    # Setup test data
    chatbot_id = "test_chatbot"
    pipeline_type = "pipeline_type1"

    empty_pipeline_handler._chatbot_configs[chatbot_id] = ChatbotConfig(
        pipeline_type=pipeline_type,
        pipeline_config={
            "supported_models": {"model1": {"name": "model1", "model_kwargs": {}, "model_env_kwargs": {}}}
        },
        prompt_builder_catalogs=None,
        lmrp_catalogs=None,
    )

    empty_pipeline_handler._plugins[pipeline_type] = mock_plugin

    # Make _build_plugin raise an exception
    with patch.object(
        PipelineHandler, "_build_plugin", new_callable=AsyncMock, side_effect=Exception("Test error")
    ) as mock_build_plugin:
        with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
            await empty_pipeline_handler._async_rebuild_plugin(chatbot_id)

            mock_build_plugin.assert_called_once()
            mock_logger.warning.assert_called_once()


@pytest.mark.asyncio
async def test_async_rebuild_pipeline_success(empty_pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Valid chatbot_id and model_id
    - Builder exists
    - Model configuration exists

    Expected:
    - _build_plugin is called with correct parameters
    - Pipeline is successfully rebuilt
    """
    # Setup test data
    chatbot_id = "test_chatbot"
    model_id = "model1"
    pipeline_type = "pipeline_type1"

    # Setup builder
    empty_pipeline_handler._builders[chatbot_id] = mock_plugin

    # Setup chatbot config
    empty_pipeline_handler._chatbot_configs[chatbot_id] = ChatbotConfig(
        pipeline_type=pipeline_type,
        pipeline_config={
            "supported_models": {"model1": {"name": "model1", "model_kwargs": {}, "model_env_kwargs": {}}}
        },
        prompt_builder_catalogs=None,
        lmrp_catalogs=None,
    )

    # Mock the _build_plugin method
    with patch.object(PipelineHandler, "_build_plugin", new_callable=AsyncMock) as mock_build_plugin:
        with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
            await empty_pipeline_handler._async_rebuild_pipeline(chatbot_id, model_id)

            # Verify _build_plugin was called with correct parameters
            mock_build_plugin.assert_called_once()
            call_args = mock_build_plugin.call_args[0]
            assert call_args[0] is empty_pipeline_handler  # self
            assert call_args[1] == chatbot_id
            assert len(call_args[2]) == 1  # model_config list
            assert call_args[3] == mock_plugin

            # Verify success was logged
            mock_logger.info.assert_called_once()


@pytest.mark.asyncio
async def test_async_rebuild_pipeline_missing_builder_rebuild_success(
    empty_pipeline_handler: PipelineHandler, mock_plugin: Mock
):
    """
    Condition:
    - Valid chatbot_id and model_id
    - Builder does not exist initially but is successfully rebuilt
    - Model configuration exists

    Expected:
    - _async_rebuild_plugin is called to rebuild the plugin
    - _build_plugin is called with correct parameters
    - Pipeline is successfully rebuilt
    """
    # Setup test data
    chatbot_id = "test_chatbot"
    model_id = "model1"
    pipeline_type = "pipeline_type1"

    # Setup chatbot config
    empty_pipeline_handler._chatbot_configs[chatbot_id] = ChatbotConfig(
        pipeline_type=pipeline_type,
        pipeline_config={
            "supported_models": {"model1": {"name": "model1", "model_kwargs": {}, "model_env_kwargs": {}}}
        },
        prompt_builder_catalogs=None,
        lmrp_catalogs=None,
    )

    # Mock _async_rebuild_plugin to add the builder
    async def mock_rebuild_plugin(chat_id):
        empty_pipeline_handler._builders[chat_id] = mock_plugin
        return None

    with patch.object(empty_pipeline_handler, "_async_rebuild_plugin", side_effect=mock_rebuild_plugin) as mock_rebuild:
        with patch.object(PipelineHandler, "_build_plugin", new_callable=AsyncMock) as mock_build_plugin:
            with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
                await empty_pipeline_handler._async_rebuild_pipeline(chatbot_id, model_id)

                # Verify _async_rebuild_plugin was called
                mock_rebuild.assert_called_once_with(chatbot_id)

                # Verify _build_plugin was called
                mock_build_plugin.assert_called_once()

                # Verify success was logged
                mock_logger.info.assert_called_once()


@pytest.mark.asyncio
async def test_async_rebuild_pipeline_missing_builder_rebuild_fails(empty_pipeline_handler: PipelineHandler):
    """
    Condition:
    - Valid chatbot_id and model_id
    - Builder does not exist and rebuild fails

    Expected:
    - _async_rebuild_plugin is called
    - Method logs warning and returns early
    - _build_plugin is not called
    """
    chatbot_id = "test_chatbot"
    model_id = "model1"

    # Setup chatbot config
    empty_pipeline_handler._chatbot_configs[chatbot_id] = ChatbotConfig(
        pipeline_type="pipeline_type1", pipeline_config={}, prompt_builder_catalogs=None, lmrp_catalogs=None
    )

    with patch.object(empty_pipeline_handler, "_async_rebuild_plugin", new_callable=AsyncMock) as mock_rebuild:
        with patch.object(PipelineHandler, "_build_plugin", new_callable=AsyncMock) as mock_build_plugin:
            with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
                await empty_pipeline_handler._async_rebuild_pipeline(chatbot_id, model_id)

                # Verify _async_rebuild_plugin was called
                mock_rebuild.assert_called_once_with(chatbot_id)

                # Verify warning was logged
                mock_logger.warning.assert_called_once()

                # Verify _build_plugin was not called
                mock_build_plugin.assert_not_called()


@pytest.mark.asyncio
async def test_async_rebuild_pipeline_chatbot_config_not_found(
    empty_pipeline_handler: PipelineHandler, mock_plugin: Mock
):
    """
    Condition:
    - Valid chatbot_id and model_id
    - Builder exists
    - Chatbot configuration not found

    Expected:
    - Method logs warning and returns early
    - _build_plugin is not called
    """
    chatbot_id = "test_chatbot"
    model_id = "model1"

    # Setup builder but no config
    empty_pipeline_handler._builders[chatbot_id] = mock_plugin

    with patch.object(PipelineHandler, "_build_plugin", new_callable=AsyncMock) as mock_build_plugin:
        with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
            await empty_pipeline_handler._async_rebuild_pipeline(chatbot_id, model_id)

            # Verify warning was logged
            mock_logger.warning.assert_called_once()

            # Verify _build_plugin was not called
            mock_build_plugin.assert_not_called()


@pytest.mark.asyncio
async def test_async_rebuild_pipeline_model_not_found(empty_pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Valid chatbot_id
    - Builder exists
    - Chatbot configuration exists
    - Model ID not found in supported models

    Expected:
    - Method logs warning and returns early
    - _build_plugin is not called
    """
    chatbot_id = "test_chatbot"
    model_id = "nonexistent_model"

    # Setup builder and config
    empty_pipeline_handler._builders[chatbot_id] = mock_plugin
    empty_pipeline_handler._chatbot_configs[chatbot_id] = ChatbotConfig(
        pipeline_type="pipeline_type1",
        pipeline_config={
            "supported_models": {"model1": {"name": "model1", "model_kwargs": {}, "model_env_kwargs": {}}}
        },
        prompt_builder_catalogs=None,
        lmrp_catalogs=None,
    )

    with patch.object(PipelineHandler, "_build_plugin", new_callable=AsyncMock) as mock_build_plugin:
        with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
            await empty_pipeline_handler._async_rebuild_pipeline(chatbot_id, model_id)

            # Verify warning was logged
            mock_logger.warning.assert_called_once()

            # Verify _build_plugin was not called
            mock_build_plugin.assert_not_called()


@pytest.mark.asyncio
async def test_async_rebuild_pipeline_model_with_model_id(empty_pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Valid chatbot_id
    - Model has model_id field instead of relying on name

    Expected:
    - Model is correctly identified by model_id
    - _build_plugin is called with correct parameters
    """
    chatbot_id = "test_chatbot"
    model_id = "custom_model_id"

    # Setup builder and config with model having model_id
    empty_pipeline_handler._builders[chatbot_id] = mock_plugin
    empty_pipeline_handler._chatbot_configs[chatbot_id] = ChatbotConfig(
        pipeline_type="pipeline_type1",
        pipeline_config={
            "supported_models": {
                "model1": {
                    "model_id": "custom_model_id",
                    "name": "different_name",
                    "model_kwargs": {},
                    "model_env_kwargs": {},
                }
            }
        },
        prompt_builder_catalogs=None,
        lmrp_catalogs=None,
    )

    with patch.object(PipelineHandler, "_build_plugin", new_callable=AsyncMock) as mock_build_plugin:
        await empty_pipeline_handler._async_rebuild_pipeline(chatbot_id, model_id)

        # Verify _build_plugin was called
        mock_build_plugin.assert_called_once()

        # Verify the correct model config was passed
        model_config = mock_build_plugin.call_args[0][2][0]
        assert model_config.get("model_id") == "custom_model_id"
        assert model_config.get("name") == "different_name"


@pytest.mark.asyncio
async def test_async_rebuild_pipeline_handles_exception(empty_pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Valid setup
    - _build_plugin raises an exception

    Expected:
    - Exception is caught and logged
    - Method completes without raising exception
    """
    chatbot_id = "test_chatbot"
    model_id = "model1"

    # Setup builder and config
    empty_pipeline_handler._builders[chatbot_id] = mock_plugin
    empty_pipeline_handler._chatbot_configs[chatbot_id] = ChatbotConfig(
        pipeline_type="pipeline_type1",
        pipeline_config={
            "supported_models": {"model1": {"name": "model1", "model_kwargs": {}, "model_env_kwargs": {}}}
        },
        prompt_builder_catalogs=None,
        lmrp_catalogs=None,
    )

    # Make _build_plugin raise an exception
    with patch.object(
        PipelineHandler, "_build_plugin", new_callable=AsyncMock, side_effect=Exception("Test error")
    ) as mock_build_plugin:
        with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
            await empty_pipeline_handler._async_rebuild_pipeline(chatbot_id, model_id)

            # Verify _build_plugin was called
            mock_build_plugin.assert_called_once()

            # Verify warning was logged
            mock_logger.warning.assert_called_once()


def test_try_rebuild_plugin_success(empty_pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Valid chatbot_id with existing configuration
    - Plugin exists for the pipeline type
    - Supported models are configured

    Expected:
    - Plugin is stored in _builders
    - Catalogs are set on the plugin
    - Success is logged
    """
    # Setup test data
    chatbot_id = "test_chatbot"
    pipeline_type = "pipeline_type1"

    mock_prompt_catalog = Mock(spec=PromptBuilderCatalog)
    mock_lmrp_catalog = Mock(spec=LMRequestProcessorCatalog)

    empty_pipeline_handler._chatbot_configs[chatbot_id] = ChatbotConfig(
        pipeline_type=pipeline_type,
        pipeline_config={
            "supported_models": {"model1": {"name": "model1", "model_kwargs": {}, "model_env_kwargs": {}}}
        },
        prompt_builder_catalogs={"default": mock_prompt_catalog},
        lmrp_catalogs={"default": mock_lmrp_catalog},
    )

    empty_pipeline_handler._plugins[pipeline_type] = mock_plugin

    with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        empty_pipeline_handler._try_rebuild_plugin(chatbot_id)

        # Verify plugin was stored in _builders
        assert chatbot_id in empty_pipeline_handler._builders
        assert empty_pipeline_handler._builders[chatbot_id] == mock_plugin

        # Verify catalogs were set on the plugin
        assert mock_plugin.prompt_builder_catalogs == {"default": mock_prompt_catalog}
        assert mock_plugin.lmrp_catalogs == {"default": mock_lmrp_catalog}

        # Verify success was logged
        mock_logger.info.assert_called_once()


def test_try_rebuild_plugin_chatbot_not_found(empty_pipeline_handler: PipelineHandler):
    """
    Condition:
    - chatbot_id not in _chatbot_configs

    Expected:
    - Method logs warning and returns early
    - No plugin is stored in _builders
    """
    with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        empty_pipeline_handler._try_rebuild_plugin("nonexistent_chatbot")

        # Verify warning was logged
        mock_logger.warning.assert_called_once()

        # Verify no plugin was stored
        assert "nonexistent_chatbot" not in empty_pipeline_handler._builders


def test_try_rebuild_plugin_plugin_not_found(empty_pipeline_handler: PipelineHandler):
    """
    Condition:
    - Valid chatbot_id with existing configuration
    - Plugin does not exist for the pipeline type

    Expected:
    - Method logs warning and returns early
    - No plugin is stored in _builders
    """
    # Setup test data
    chatbot_id = "test_chatbot"
    pipeline_type = "unknown_pipeline_type"

    empty_pipeline_handler._chatbot_configs[chatbot_id] = ChatbotConfig(
        pipeline_type=pipeline_type, pipeline_config={}, prompt_builder_catalogs=None, lmrp_catalogs=None
    )

    with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        empty_pipeline_handler._try_rebuild_plugin(chatbot_id)

        # Verify warning was logged
        mock_logger.warning.assert_called_once()

        # Verify no plugin was stored
        assert chatbot_id not in empty_pipeline_handler._builders


def test_try_rebuild_plugin_no_supported_models(empty_pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Valid chatbot_id with existing configuration
    - Plugin exists for the pipeline type
    - No supported models in configuration

    Expected:
    - Method logs warning and returns early
    - No plugin is stored in _builders
    """
    # Setup test data
    chatbot_id = "test_chatbot"
    pipeline_type = "pipeline_type1"

    empty_pipeline_handler._chatbot_configs[chatbot_id] = ChatbotConfig(
        pipeline_type=pipeline_type,
        pipeline_config={"supported_models": {}},  # Empty supported_models
        prompt_builder_catalogs=None,
        lmrp_catalogs=None,
    )

    empty_pipeline_handler._plugins[pipeline_type] = mock_plugin

    with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        empty_pipeline_handler._try_rebuild_plugin(chatbot_id)

        # Verify warning was logged
        mock_logger.warning.assert_called_once()

        # Verify no plugin was stored
        assert chatbot_id not in empty_pipeline_handler._builders


def test_try_rebuild_plugin_handles_exception(empty_pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Valid setup but plugin manipulation raises an exception

    Expected:
    - Exception is caught and logged
    - Method completes without raising exception
    """
    # Setup test data
    chatbot_id = "test_chatbot"
    pipeline_type = "pipeline_type1"

    empty_pipeline_handler._chatbot_configs[chatbot_id] = ChatbotConfig(
        pipeline_type=pipeline_type,
        pipeline_config={
            "supported_models": {"model1": {"name": "model1", "model_kwargs": {}, "model_env_kwargs": {}}}
        },
        prompt_builder_catalogs=None,
        lmrp_catalogs=None,
    )

    # Create a plugin that raises an exception when setting prompt_builder_catalogs
    mock_plugin_with_error = Mock(spec=Plugin)
    type(mock_plugin_with_error).prompt_builder_catalogs = property(
        fget=lambda x: None,
        fset=lambda x, y: exec('raise Exception("Test error")'),
    )

    empty_pipeline_handler._plugins[pipeline_type] = mock_plugin_with_error

    with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        empty_pipeline_handler._try_rebuild_plugin(chatbot_id)

        # Verify warning was logged
        mock_logger.warning.assert_called_once()

        # Verify no plugin was stored
        assert chatbot_id not in empty_pipeline_handler._builders


def test_get_pipeline_builder_success(empty_pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Valid chatbot_id with existing builder in _builders

    Expected:
    - Returns the correct builder without attempting to rebuild
    """
    # Setup test data
    chatbot_id = "test_chatbot"
    empty_pipeline_handler._builders[chatbot_id] = mock_plugin

    # Patch _try_rebuild_plugin to verify it's not called
    with patch.object(empty_pipeline_handler, "_try_rebuild_plugin") as mock_rebuild:
        result = empty_pipeline_handler.get_pipeline_builder(chatbot_id)

        # Verify correct builder is returned
        assert result == mock_plugin

        # Verify rebuild was not attempted
        mock_rebuild.assert_not_called()


def test_get_pipeline_builder_rebuild_success(empty_pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - chatbot_id not in _builders initially
    - _try_rebuild_plugin successfully adds the builder

    Expected:
    - _try_rebuild_plugin is called
    - Returns the newly built builder
    """
    # Setup test data
    chatbot_id = "test_chatbot"

    # Define mock behavior to add the builder when _try_rebuild_plugin is called
    def mock_rebuild_side_effect(chat_id):
        empty_pipeline_handler._builders[chat_id] = mock_plugin

    # Patch _try_rebuild_plugin with the side effect
    with patch.object(
        empty_pipeline_handler, "_try_rebuild_plugin", side_effect=mock_rebuild_side_effect
    ) as mock_rebuild:
        result = empty_pipeline_handler.get_pipeline_builder(chatbot_id)

        # Verify rebuild was attempted
        mock_rebuild.assert_called_once_with(chatbot_id)

        # Verify correct builder is returned
        assert result == mock_plugin


def test_get_pipeline_builder_rebuild_fails(empty_pipeline_handler: PipelineHandler):
    """
    Condition:
    - chatbot_id not in _builders initially
    - _try_rebuild_plugin fails to add the builder

    Expected:
    - _try_rebuild_plugin is called
    - Raises ValueError with appropriate message
    """
    # Setup test data
    chatbot_id = "test_chatbot"

    # Patch _try_rebuild_plugin (default implementation won't add any builder)
    with patch.object(empty_pipeline_handler, "_try_rebuild_plugin") as mock_rebuild:
        # Verify ValueError is raised
        with pytest.raises(
            ValueError, match=f"Pipeline builder for chatbot `{chatbot_id}` not found and could not be rebuilt"
        ):
            empty_pipeline_handler.get_pipeline_builder(chatbot_id)

        # Verify rebuild was attempted
        mock_rebuild.assert_called_once_with(chatbot_id)


def test_get_pipeline_builder_with_logger(empty_pipeline_handler: PipelineHandler):
    """
    Condition:
    - chatbot_id not in _builders initially

    Expected:
    - Warning is logged before attempting rebuild
    """
    # Setup test data
    chatbot_id = "test_chatbot"

    # Patch logger and _try_rebuild_plugin
    with patch("glchat_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        with patch.object(empty_pipeline_handler, "_try_rebuild_plugin"):
            # This will raise ValueError, but we're just testing the logging
            with pytest.raises(ValueError):
                empty_pipeline_handler.get_pipeline_builder(chatbot_id)

            # Verify warning was logged
            mock_logger.warning.assert_called_once()
