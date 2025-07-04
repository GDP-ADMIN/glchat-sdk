"""Unit tests for PipelineHandler class."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from bosa_core import Plugin
from gllm_inference.catalog import LMRequestProcessorCatalog, PromptBuilderCatalog
from gllm_pipeline.pipeline.pipeline import Pipeline

from gllm_plugin.config.app_config import AppConfig
from gllm_plugin.pipeline.pipeline_handler import (
    ChatbotConfig,
    ChatbotPresetMapping,
    PipelineHandler,
    PipelinePresetConfig,
)
from gllm_plugin.storage.base_chat_history_storage import BaseChatHistoryStorage


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
                ],
            )
        },
    )

    await PipelineHandler.ainitialize_plugin(pipeline_handler, mock_plugin)

    assert "pipeline_type1" in pipeline_handler._plugins
    assert pipeline_handler._plugins["pipeline_type1"] == mock_plugin
    assert ("chatbot1", "gpt-3") in pipeline_handler._pipeline_cache
    assert ("chatbot1", "gpt-4") in pipeline_handler._pipeline_cache
    assert mock_plugin.build.call_count == 2


@pytest.mark.asyncio
async def test_ainitialize_plugin_no_matching_config(pipeline_handler: PipelineHandler, mock_plugin: Mock):
    """
    Condition:
    - Plugin type not in activated configs

    Expected:
    - Method returns early without building pipelines
    """
    mock_plugin.name = "unknown_type"

    await PipelineHandler.ainitialize_plugin(pipeline_handler, mock_plugin)

    assert "unknown_type" not in pipeline_handler._plugins
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

    with patch("gllm_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        await PipelineHandler.ainitialize_plugin(empty_pipeline_handler, mock_plugin)

        assert mock_logger.error.called
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

    with patch("gllm_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        await PipelineHandler.acleanup_plugins(pipeline_handler)

        assert mock_logger.error.called
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


def test_get_pipeline_builder_success(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Valid chatbot_id with existing builder

    Expected:
    - Returns correct plugin builder
    """
    mock_builder = Mock(spec=Plugin)
    pipeline_handler._builders["chatbot1"] = mock_builder

    result = pipeline_handler.get_pipeline_builder("chatbot1")

    assert result == mock_builder


def test_get_pipeline_builder_not_found(pipeline_handler: PipelineHandler):
    """
    Condition:
    - chatbot_id not in _builders and rebuild fails

    Expected:
    - Raises ValueError with descriptive message
    """
    with pytest.raises(ValueError, match="Pipeline builder for chatbot `nonexistent` not found and could not be rebuilt"):
        pipeline_handler.get_pipeline_builder("nonexistent")


def test_get_pipeline_success(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Valid chatbot_id and model_name with cached pipeline

    Expected:
    - Returns correct pipeline instance
    """
    mock_pipeline = Mock(spec=Pipeline)
    pipeline_handler._pipeline_cache[("chatbot1", "gpt-3")] = mock_pipeline

    result = pipeline_handler.get_pipeline("chatbot1", "gpt-3")

    assert result == mock_pipeline


def test_get_pipeline_not_found(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Pipeline key not in cache and rebuild fails

    Expected:
    - Raises ValueError with descriptive message
    """
    with pytest.raises(ValueError, match="Pipeline for chatbot `chatbot1` model `nonexistent_model` not found and could not be rebuilt"):
        pipeline_handler.get_pipeline("chatbot1", "nonexistent_model")


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

    with patch("gllm_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        await empty_pipeline_handler.create_chatbot(new_app_config, "new_chatbot")

        assert mock_logger.warning.called
        assert "new_chatbot" not in empty_pipeline_handler._chatbot_configs


@pytest.mark.asyncio
async def test_create_chatbot_no_matching_plugin(pipeline_handler: PipelineHandler):
    """
    Condition:
    - Pipeline type has no matching plugin

    Expected:
    - Method logs warning and returns early
    """
    new_app_config = Mock(spec=AppConfig)
    new_app_config.chatbots = {
        "new_chatbot": Mock(
            pipeline={"type": "unknown_type", "config": {}, "prompt_builder_catalogs": None, "lmrp_catalogs": None}
        )
    }

    with patch("gllm_plugin.pipeline.pipeline_handler.logger") as mock_logger:
        await pipeline_handler.create_chatbot(new_app_config, "new_chatbot")

        assert mock_logger.warning.called


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

    with patch("gllm_plugin.pipeline.pipeline_handler.logger") as mock_logger:
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
def test_get_pipeline_handles_different_model_types(
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

    result = pipeline_handler.get_pipeline("chatbot1", model_name)

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
