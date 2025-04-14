"""Tests for the ToolPlugin base class.

This module tests the functionality of the ToolPlugin class which serves as the base
for tool plugins in the system.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from unittest.mock import MagicMock

from bosa_core.plugin.handler import PluginHandler
from langchain_core.tools import BaseTool

from gllm_plugin.tools.tool_plugin import (
    ToolPlugin,
)


# Concrete implementation for testing
class TestToolPlugin(ToolPlugin):
    """Test implementation of ToolPlugin for testing."""

    name = "test_tool_plugin"
    description = "A test tool plugin"
    version = "1.0.0"

    def create_tool(self, **kwargs):
        """Create a simple mock tool."""
        mock_tool = MagicMock(spec=BaseTool)
        mock_tool.name = "test_tool"
        mock_tool.description = "A test tool"
        for key, value in kwargs.items():
            setattr(mock_tool, key, value)
        return mock_tool


def test_tool_plugin_attributes():
    """Test that ToolPlugin attributes are properly set."""
    plugin = TestToolPlugin()

    assert plugin.name == "test_tool_plugin"
    assert plugin.description == "A test tool plugin"
    assert plugin.version == "1.0.0"


def test_get_handler_type():
    """Test that get_handler_type returns the correct type."""
    plugin = TestToolPlugin()

    handler_type = plugin.get_handler_type()

    assert handler_type == PluginHandler
    assert issubclass(PluginHandler, handler_type)


def test_create_tool():
    """Test that create_tool returns a proper tool instance."""
    plugin = TestToolPlugin()

    tool = plugin.create_tool(custom_attr="test_value")

    assert tool.name == "test_tool"
    assert tool.description == "A test tool"
    assert tool.custom_attr == "test_value"


def test_get_tool_class():
    """Test that the tool_plugin's abstract method implementation of create_tool."""

    # Create a minimal test implementation
    class MinimalToolPlugin(ToolPlugin):
        name = "minimal_plugin"
        description = "A minimal tool plugin for testing"

        def create_tool(self, **kwargs):
            """Implement the required abstract method."""
            from langchain_core.tools import Tool

            return Tool(name="test_tool", description="Test tool", func=lambda x: "test result")

    plugin = MinimalToolPlugin()
    plugin.create_tool()  # This will cover line 61 (the pass statement in the base class)

    # Verify that get_tool_class returns the Tool class
    from langchain_core.tools import Tool

    assert plugin.get_tool_class() == Tool


def test_create_tool_instance():
    """Test that create_tool_instance calls create_tool."""
    plugin = TestToolPlugin()

    # Create a spy on the create_tool method
    original_create_tool = plugin.create_tool
    called_with_args = {}

    def spy_create_tool(**kwargs):
        nonlocal called_with_args
        called_with_args = kwargs
        return original_create_tool(**kwargs)

    plugin.create_tool = spy_create_tool

    plugin.create_tool_instance(test_arg="test_value")

    assert called_with_args.get("test_arg") == "test_value"
