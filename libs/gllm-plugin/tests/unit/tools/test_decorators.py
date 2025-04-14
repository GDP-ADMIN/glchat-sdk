"""Tests for the Tool Plugin decorator system.

This module tests the decorator-based tool plugin registration system.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from typing import Any, Optional
from unittest.mock import patch

import pytest
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from gllm_plugin.tools.decorators import (
    tool_plugin,
)


# Mock input schema for testing
class TestInput(BaseModel):
    """Test input schema for decorator tests."""

    test_param: str = Field(description="Test parameter")


@patch("gllm_agents.plugins.decorators.register_tool_plugin")
def test_tool_plugin_decorator_basic(mock_register):
    """Test the basic functionality of the tool_plugin decorator."""

    # Define a tool class with the decorator
    @tool_plugin(version="1.0.0")
    class TestTool(BaseTool):
        name: str = "test_tool"
        description: str = "Test tool description"

        def _run(self, test_param: str) -> str:
            return f"Processed: {test_param}"

    # Check that the tool class was properly modified
    assert hasattr(TestTool, "_plugin_class")

    # Check that the plugin class was created correctly
    plugin_class = TestTool._plugin_class
    assert plugin_class.name == "unknown_tool_plugin"
    assert plugin_class.description == "No description provided"
    assert plugin_class.version == "1.0.0"

    # Check that register_tool_plugin was called
    mock_register.assert_called_once()

    # Create an instance to test the create_tool method
    plugin_instance = plugin_class()
    tool_instance = plugin_instance.create_tool()

    assert isinstance(tool_instance, TestTool)
    assert tool_instance.name == "test_tool"
    assert tool_instance.description == "Test tool description"


@patch("gllm_agents.plugins.decorators.register_tool_plugin")
def test_tool_plugin_decorator_with_custom_values(mock_register):
    """Test the tool_plugin decorator with custom name and description."""

    @tool_plugin(
        version="2.0.0",
        name="custom_plugin_name",
        description="Custom plugin description",
    )
    class CustomTool(BaseTool):
        name: str = "custom_tool"
        description: str = "Custom tool description"

        def _run(self, **kwargs: Any) -> str:
            return "Custom result"

    # Check that the plugin class was created with custom values
    plugin_class = CustomTool._plugin_class
    assert plugin_class.name == "custom_plugin_name"
    assert plugin_class.description == "Custom plugin description"
    assert plugin_class.version == "2.0.0"

    # Check registration was called
    mock_register.assert_called_once()


def test_tool_plugin_decorator_with_invalid_class():
    """Test that the decorator raises an error when used on a non-BaseTool class."""
    with pytest.raises(TypeError):

        @tool_plugin(version="1.0.0")
        class NotATool:
            pass


@patch("gllm_agents.plugins.decorators.register_tool_plugin")
def test_tool_plugin_decorator_registers_correctly(mock_register):
    """Test that the decorator correctly registers the tool plugin."""

    # Define a tool class with the decorator
    @tool_plugin(version="1.0.0")
    class RegisteredTool(BaseTool):
        name: str = "registered_tool"
        description: str = "Tool for testing registration"

        def _run(self, **kwargs: Any) -> str:
            return "Registered result"

    # Check that register_tool_plugin was called with the correct class
    mock_register.assert_called_once()
    registered_class = mock_register.call_args[0][0]

    # Verify the registered class is the plugin class
    assert registered_class.__name__ == "RegisteredToolPlugin"
    assert registered_class.name == "unknown_tool_plugin"


@patch("gllm_agents.plugins.decorators.register_tool_plugin")
def test_tool_plugin_decorator_creates_plugin_with_create_tool(mock_register):
    """Test that the plugin's create_tool method properly instantiates the tool."""

    @tool_plugin(version="1.0.0")
    class ToolWithArgs(BaseTool):
        name: str = "tool_with_args"
        description: str = "Tool that accepts arguments"
        custom_arg: Optional[str] = None

        def __init__(self, custom_arg=None, **kwargs):
            super().__init__(**kwargs)
            self.custom_arg = custom_arg

        def _run(self, **kwargs: Any) -> str:
            return f"Custom arg: {self.custom_arg}"

    # Get the plugin class and create an instance
    plugin_class = ToolWithArgs._plugin_class
    plugin_instance = plugin_class()

    # Test that create_tool properly passes arguments
    tool = plugin_instance.create_tool(custom_arg="test_value")
    assert isinstance(tool, ToolWithArgs)
    assert tool.custom_arg == "test_value"

    # Test tool functionality
    result = tool._run()
    assert result == "Custom arg: test_value"
