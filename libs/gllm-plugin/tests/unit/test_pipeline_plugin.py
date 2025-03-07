"""Unit tests for PipelineBuilderPlugin.

This module contains tests for the base PipelineBuilderPlugin class.
"""

from dataclasses import field
from unittest.mock import Mock

import pytest
from gllm_inference.catalog.catalog import BaseCatalog
from gllm_inference.multimodal_prompt_builder import MultimodalPromptBuilder
from gllm_inference.prompt_builder.prompt_builder import BasePromptBuilder
from gllm_pipeline.pipeline.pipeline import Pipeline
from pydantic import BaseModel

from gllm_plugin.config.app_config import AppConfig
from gllm_plugin.pipeline.pipeline_plugin import PipelineBuilderPlugin
from gllm_plugin.supported_models import Provider


class TestPipelineState:
    """Test pipeline state class."""

    pass


class TestPipelinePresetConfig:
    """Test pipeline preset config class."""

    pipeline_preset_id: str = "test_preset"
    supported_models: dict[str, dict] = field(default_factory=lambda: {"openai/gpt-4o": {"max_tokens": 100}})
    supported_agents: list[str] = []
    support_pii_anonymization: bool = False
    support_multimodal: bool = False
    use_docproc: bool = False
    search_types: list[str] = field(default_factory=lambda: ["test_search"])
    test_field: str = "test"


class TestPipelineRuntimeConfig(BaseModel):
    """Test pipeline runtime config class."""

    runtime_field: str


class TestPipelineBuilderPlugin(PipelineBuilderPlugin[TestPipelineState, TestPipelinePresetConfig]):
    """Test implementation of PipelineBuilderPlugin."""

    name = "test_pipeline"
    description = "Test pipeline builder plugin"
    version = "1.0.0"
    preset_config_class = TestPipelinePresetConfig
    additional_config_class = TestPipelineRuntimeConfig

    def build_initial_state(self, request_config: dict, pipeline_config: dict, **kwargs) -> TestPipelineState:
        """Build initial pipeline state."""
        return TestPipelineState()

    def build(self, pipeline_config: dict) -> Pipeline:
        """Build pipeline instance."""
        return Mock(spec=Pipeline)


@pytest.fixture
def mock_app_config():
    """Create a mock AppConfig."""
    return Mock(spec=AppConfig)


@pytest.fixture
def mock_catalog():
    """Create a mock catalog."""
    catalog = Mock(spec=BaseCatalog)
    catalog.components = {
        "test_prompt": Mock(spec=BasePromptBuilder),
        "test_prompt_openai": Mock(spec=BasePromptBuilder),
        "multimodal_prompt": Mock(spec=MultimodalPromptBuilder),
    }
    return catalog


@pytest.fixture
def pipeline_plugin(mock_app_config, mock_catalog):
    """Create a pipeline plugin instance."""
    plugin = TestPipelineBuilderPlugin()
    plugin.app_config = mock_app_config
    plugin.catalog = mock_catalog
    return plugin


def test_get_preset_config_class_with_class():
    """Test getting preset config class when it's defined."""
    assert TestPipelineBuilderPlugin.get_preset_config_class() == TestPipelinePresetConfig


def test_get_preset_config_class_without_class():
    """Test getting preset config class when it's not defined."""

    class EmptyPlugin(PipelineBuilderPlugin):
        name = "empty"
        preset_config_class = None

    with pytest.raises(NotImplementedError, match="EmptyPlugin must define a `preset_config_class` attribute"):
        EmptyPlugin.get_preset_config_class()


def test_build_initial_state(pipeline_plugin):
    """Test building initial pipeline state."""
    request_config = {"test": "value"}
    pipeline_config = {"model": "test-model"}

    state = pipeline_plugin.build_initial_state(request_config, pipeline_config)
    assert isinstance(state, TestPipelineState)


def test_build(pipeline_plugin):
    """Test building pipeline instance."""
    pipeline_config = {"model": "test-model"}
    pipeline = pipeline_plugin.build(pipeline_config)
    assert isinstance(pipeline, Mock)
    assert isinstance(pipeline, Pipeline)


def test_build_additional_runtime_config_with_config(pipeline_plugin):
    """Test building additional runtime config when config class is defined."""
    pipeline_config = {"runtime_field": "test_value"}
    config = pipeline_plugin.build_additional_runtime_config(pipeline_config)
    assert config == {"runtime_field": "test_value"}


def test_build_additional_runtime_config_without_config():
    """Test building additional runtime config when config class is not defined."""

    class EmptyPlugin(TestPipelineBuilderPlugin):
        additional_config_class = None

    plugin = EmptyPlugin()
    config = plugin.build_additional_runtime_config({})
    assert config == {}


def test_get_config_without_preset():
    """Test getting config when preset config is not defined."""

    class EmptyPlugin(TestPipelineBuilderPlugin):
        preset_config_class = None

    plugin = EmptyPlugin()
    config = plugin.get_config()
    assert config == {}
