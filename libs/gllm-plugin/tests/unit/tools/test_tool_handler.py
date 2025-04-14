"""Tests for the Tool Handler.

This module tests the ToolHandler class which manages tool plugins and provides
registry services for the system.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from typing import Any, Optional
from unittest.mock import MagicMock, call, patch

from langchain_core.tools import BaseTool
from pydantic import Field

from gllm_plugin.tools.tool_handler import (
    ToolHandler,
    get_plugin_manager,
    get_tool_handler,
    initialize_tool_plugins,
)
from gllm_plugin.tools.tool_plugin import (
    ToolPlugin,
)


# Mock tool for testing
class MockTool(BaseTool):
    """Mock tool for testing the tool handler."""

    name: str = "mock_tool"
    description: str = "A mock tool for testing"
    api_key: Optional[str] = Field(default=None)

    def _run(self, **kwargs: Any) -> str:
        return "Mock tool result"


# Mock plugin for testing
class MockToolPlugin(ToolPlugin):
    """Mock plugin for testing the tool handler."""

    name = "mock_plugin"
    description = "A mock plugin for testing"

    def create_tool(self, **kwargs):
        tool = MockTool()
        # Add any kwargs as attributes
        for key, value in kwargs.items():
            if hasattr(tool, key):
                setattr(tool, key, value)
        return tool


def test_tool_handler_init():
    """Test that ToolHandler initializes correctly."""
    handler = ToolHandler(test_config="value")

    assert handler.config_kwargs == {"test_config": "value"}
    assert handler._tool_registry == {}
    assert handler._tool_instances == {}


def test_create_injections():
    """Test that create_injections returns an empty dict."""
    handler = ToolHandler()

    injections = ToolHandler.create_injections(handler)

    assert isinstance(injections, dict)
    assert len(injections) == 0


def test_initialize_plugin():
    """Test that initialize_plugin correctly sets up a plugin."""
    handler = ToolHandler()
    plugin = MockToolPlugin()

    ToolHandler.initialize_plugin(handler, plugin)

    # Check registry entries
    assert handler._tool_registry["mock_plugin"] == plugin
    assert "mock_tool" in handler._tool_instances

    # Check that the tool instance was created correctly
    tool = handler._tool_instances["mock_tool"]
    assert isinstance(tool, MockTool)
    assert tool.name == "mock_tool"


def test_initialize_plugin_with_non_tool_plugin():
    """Test that initialize_plugin safely handles non-ToolPlugin instances."""
    handler = ToolHandler()
    not_a_plugin = MagicMock()
    not_a_plugin.name = "not_a_plugin"

    # This should not raise an exception
    ToolHandler.initialize_plugin(handler, not_a_plugin)

    # The plugin should not be registered
    assert "not_a_plugin" not in handler._tool_registry
    assert len(handler._tool_instances) == 0


def test_initialize_plugin_with_config():
    """Test that initialize_plugin passes config to create_tool_instance."""
    handler = ToolHandler(api_key="test_key")
    plugin = MockToolPlugin()

    ToolHandler.initialize_plugin(handler, plugin)

    # Get the tool and check it received the config
    tool = handler._tool_instances["mock_tool"]
    assert tool.api_key == "test_key"


def test_get_tool():
    """Test that get_tool returns the correct tool."""
    handler = ToolHandler()
    mock_tool = MockTool()

    # Add a tool directly
    handler._tool_instances["mock_tool"] = mock_tool

    # Get the tool
    retrieved_tool = handler.get_tool("mock_tool")

    assert retrieved_tool == mock_tool

    # Test getting a non-existent tool
    non_existent = handler.get_tool("non_existent")
    assert non_existent is None


def test_get_all_tools():
    """Test that get_all_tools returns all registered tools."""
    handler = ToolHandler()

    # Add some tools
    tool1 = MockTool()
    tool1.name = "tool1"
    tool2 = MockTool()
    tool2.name = "tool2"

    handler._tool_instances = {"tool1": tool1, "tool2": tool2}

    # Get all tools
    tools = handler.get_all_tools()

    assert len(tools) == 2
    assert tool1 in tools
    assert tool2 in tools


def test_register_tool_instance():
    """Test that register_tool_instance adds a tool."""
    handler = ToolHandler()
    tool = MockTool()

    handler.register_tool_instance("custom_name", tool)

    assert handler._tool_instances["custom_name"] == tool


@patch("gllm_agents.plugins.tool_handler.PluginManager")
def test_get_tool_handler(mock_plugin_manager):
    """Test that get_tool_handler retrieves the handler from the plugin manager."""
    # Setup a mock handler
    mock_handler = MagicMock(spec=ToolHandler)

    # Setup the mock plugin manager
    mock_manager_instance = mock_plugin_manager.return_value
    mock_manager_instance.get_handler.return_value = mock_handler

    # Call the function
    handler = get_tool_handler()

    # Verify interactions
    mock_plugin_manager.assert_called_once()
    mock_manager_instance.get_handler.assert_called_once_with(ToolHandler)
    assert handler == mock_handler


@patch("gllm_agents.plugins.tool_handler.PluginManager")
def test_get_tool_handler_error(mock_plugin_manager):
    """Test that get_tool_handler handles errors gracefully."""
    # Setup the mock to raise an exception
    mock_manager_instance = mock_plugin_manager.return_value
    mock_manager_instance.get_handler.side_effect = Exception("Test error")

    # Call the function
    handler = get_tool_handler()

    # Verify interactions
    mock_plugin_manager.assert_called_once()
    mock_manager_instance.get_handler.assert_called_once_with(ToolHandler)
    assert handler is None


@patch("gllm_agents.plugins.tool_handler.PluginManager")
def test_get_plugin_manager(mock_plugin_manager):
    """Test that get_plugin_manager returns a plugin manager instance."""
    # Call the function
    manager = get_plugin_manager()

    # Verify interactions
    mock_plugin_manager.assert_called_once()
    assert manager == mock_plugin_manager.return_value


@patch("gllm_agents.plugins.tool_handler.PluginManager")
@patch("gllm_agents.plugins.plugin.AGENT_TOOL_PLUGINS")
def test_initialize_tool_plugins(mock_agent_tool_plugins, mock_plugin_manager):
    """Test that initialize_tool_plugins sets everything up correctly."""
    # Setup mocks
    mock_manager_instance = mock_plugin_manager.return_value

    # Mock the import of plugins
    mock_plugin_class1 = MagicMock()
    mock_plugin_class1.__name__ = "MockPlugin1"
    mock_plugin_class2 = MagicMock()
    mock_plugin_class2.__name__ = "MockPlugin2"

    # Create a patch to mock the plugin registry
    with patch(
        "gllm_agents.plugins.plugin.AGENT_TOOL_PLUGINS",
        [mock_plugin_class1, mock_plugin_class2],
    ):
        # Call the function
        handler = initialize_tool_plugins(test_config="value")

        # Verify interactions
        mock_plugin_manager.assert_called_once()
        assert mock_manager_instance.register_plugin.call_count == 2
        mock_manager_instance.register_plugin.assert_has_calls([call(mock_plugin_class1), call(mock_plugin_class2)])

        # Verify handler was created with config
        assert isinstance(handler, ToolHandler)
        assert handler.config_kwargs == {"test_config": "value"}


@patch("gllm_agents.plugins.tool_handler.PluginManager")
@patch("gllm_agents.plugins.plugin.AGENT_TOOL_PLUGINS")
def test_initialize_tool_plugins_with_failing_plugin(mock_agent_tool_plugins, mock_plugin_manager):
    """Test that initialize_tool_plugins handles plugin registration failures gracefully."""
    # Create a mock plugin manager instance
    mock_manager_instance = MagicMock()
    mock_plugin_manager.return_value = mock_manager_instance

    # Set up our plugin manager to raise an exception for plugin registration
    mock_manager_instance.register_plugin.side_effect = Exception("Test plugin registration failure")

    # Create a test plugin class to add to AGENT_TOOL_PLUGINS
    class TestFailingPlugin(ToolPlugin):
        name = "test_failing_plugin"
        description = "A plugin that fails during registration"

        def create_tool(self, **kwargs):
            return MagicMock(spec=BaseTool)

    # Set up the mocked AGENT_TOOL_PLUGINS to return our test plugin
    mock_agent_tool_plugins.__iter__.return_value = [TestFailingPlugin]

    # The function should still succeed even when plugin registration fails
    handler = initialize_tool_plugins()

    # Verify that register_plugin was called (and failed as expected)
    mock_manager_instance.register_plugin.assert_called_once_with(TestFailingPlugin)

    # Verify we got back a valid tool handler
    assert isinstance(handler, ToolHandler)
