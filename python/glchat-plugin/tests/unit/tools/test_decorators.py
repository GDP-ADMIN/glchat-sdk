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

from glchat_plugin.tools.decorators import (
    get_plugin_metadata,
    is_tool_plugin,
    tool_plugin,
)


class TestInput(BaseModel):
    """Test input schema for decorator tests."""

    test_param: str = Field(description="Test parameter")


@patch("glchat_plugin.tools.decorators.logger")
def test_tool_plugin_decorator_basic(mock_logger):
    """Test the basic functionality of the tool_plugin decorator.

    Condition:
        - A BaseTool subclass is decorated with @tool_plugin
        - The version is set to "1.0.0"
        - The decorated tool has standard name and description attributes
        - The tool is instantiated and its _run method is called

    Expected:
        - The tool class should have _is_tool_plugin attribute set to True
        - The tool class should have _plugin_metadata with correct version
        - The tool instance should maintain normal BaseTool functionality
        - The logger should be called to record the tool marking
    """

    # Define a tool class with the decorator
    @tool_plugin(version="1.0.0")
    class TestTool(BaseTool):
        name: str = "test_tool"
        description: str = "Test tool description"

        def _run(self, test_param: str) -> str:
            return f"Processed: {test_param}"

    # Check that the tool class was properly decorated
    assert hasattr(TestTool, "_is_tool_plugin")
    assert hasattr(TestTool, "_plugin_metadata")
    assert TestTool._is_tool_plugin is True

    # Check plugin metadata (only basic info now)
    metadata = TestTool._plugin_metadata
    assert metadata["version"] == "1.0.0"

    # Create an instance to verify functionality
    tool_instance = TestTool()
    assert tool_instance.name == "test_tool"
    assert tool_instance.description == "Test tool description"
    result = tool_instance._run(test_param="test")
    assert result == "Processed: test"

    # Verify logger was called
    mock_logger.info.assert_called()


@patch("glchat_plugin.tools.decorators.logger")
def test_tool_plugin_decorator_with_invalid_class(mock_logger):
    """Test that the decorator raises an error when used on a non-BaseTool class.

    Condition:
        - A regular class that doesn't inherit from BaseTool is decorated
        - The @tool_plugin decorator is applied with version "1.0.0"

    Expected:
        - TypeError should be raised with a message indicating the class is not a subclass of BaseTool
    """
    with pytest.raises(TypeError, match="is not a subclass of BaseTool"):

        @tool_plugin(version="1.0.0")
        class NotATool:
            pass


@patch("glchat_plugin.tools.decorators.logger")
def test_is_tool_plugin_function(mock_logger):
    """Test the is_tool_plugin helper function.

    Condition:
        - A BaseTool subclass is decorated with @tool_plugin
        - Another BaseTool subclass is not decorated
        - Various non-class objects are tested

    Expected:
        - is_tool_plugin returns True only for the decorated tool class
        - is_tool_plugin returns False for undecorated classes
        - is_tool_plugin returns False for non-class objects and None
        - The logger is called for the decoration process
    """

    @tool_plugin(version="1.0.0")
    class DecoratedTool(BaseTool):
        name: str = "decorated_tool"
        description: str = "Decorated tool"

        def _run(self, **kwargs: Any) -> str:
            return "Test"

    class UndecoratedTool(BaseTool):
        name: str = "undecorated_tool"
        description: str = "Undecorated tool"

        def _run(self, **kwargs: Any) -> str:
            return "Test"

    # Test various cases
    assert is_tool_plugin(DecoratedTool) is True
    assert is_tool_plugin(UndecoratedTool) is False
    assert is_tool_plugin("not a class") is False
    assert is_tool_plugin(None) is False

    # Verify logger was called
    mock_logger.info.assert_called()


@patch("glchat_plugin.tools.decorators.logger")
def test_get_plugin_metadata(mock_logger):
    """Test the get_plugin_metadata helper function.

    Condition:
        - A BaseTool subclass is decorated with @tool_plugin and version "1.0.0"
        - Another BaseTool subclass is not decorated
        - get_plugin_metadata is called on both classes

    Expected:
        - get_plugin_metadata returns correct metadata for decorated class
        - Metadata contains the version "1.0.0"
        - ValueError is raised when called on an undecorated class
        - The logger is called during the decoration process
    """

    @tool_plugin(version="1.0.0")
    class MetadataTool(BaseTool):
        name: str = "metadata_tool"
        description: str = "Metadata tool description"

        def _run(self, **kwargs: Any) -> str:
            return "Test"

    # Test getting metadata from decorated class
    metadata = get_plugin_metadata(MetadataTool)
    assert metadata["version"] == "1.0.0"

    # Test error when getting metadata from undecorated class
    class UndecoratedTool(BaseTool):
        name: str = "undecorated"
        description: str = "Undecorated tool"

        def _run(self, **kwargs: Any) -> str:
            return "Test"

    with pytest.raises(ValueError, match="is not a decorated tool plugin"):
        get_plugin_metadata(UndecoratedTool)

    # Verify logger was called
    mock_logger.info.assert_called()


@patch("glchat_plugin.tools.decorators.logger")
def test_tool_plugin_with_args(mock_logger):
    """Test that the tool plugin works with tools that take constructor arguments.

    Condition:
        - A BaseTool subclass with custom constructor arguments is decorated
        - The tool is instantiated with a custom argument value
        - The tool's _run method uses the custom argument

    Expected:
        - The tool is properly decorated with metadata
        - The tool instance correctly stores and uses the custom argument
        - The plugin metadata contains the correct version
        - The logger is called during the decoration process
    """

    @tool_plugin(version="1.0.0")
    class ToolWithArgs(BaseTool):
        name: str = "tool_with_args"
        description: str = "Tool that accepts arguments"
        custom_arg: Optional[str] = None

        def __init__(self, custom_arg: Optional[str] = None, **kwargs):
            super().__init__(**kwargs)
            self.custom_arg = custom_arg

        def _run(self, **kwargs: Any) -> str:
            return f"Custom arg: {self.custom_arg}"

    # Create instance with arguments
    tool = ToolWithArgs(custom_arg="test_value")
    assert tool.custom_arg == "test_value"
    assert tool._run() == "Custom arg: test_value"

    # Verify plugin metadata is still correct (basic info only)
    metadata = ToolWithArgs._plugin_metadata
    assert metadata["version"] == "1.0.0"

    # Verify logger was called
    mock_logger.info.assert_called()


@patch("glchat_plugin.tools.decorators.logger")
def test_tool_plugin_decorator_logging_failure(mock_logger):
    """Test that the decorator handles logging failures gracefully.

    Condition:
        - The logger is configured to raise an exception when info is called
        - A BaseTool subclass is decorated with @tool_plugin

    Expected:
        - The decoration process completes successfully despite the logging error
        - The tool class has the _is_tool_plugin attribute set to True
        - The tool class has _plugin_metadata with the correct version
        - No exceptions are propagated from the decorator
        - The logger.info method was called exactly once
    """

    # Configure the mock logger's info method to raise an exception
    mock_logger.info.side_effect = Exception("Simulated logging error")

    try:

        @tool_plugin(version="1.0.0")
        class LoggingFailTool(BaseTool):
            name: str = "logging_fail_tool"
            description: str = "Tool designed to test logging failure"

            def _run(self, **kwargs: Any) -> str:
                return "Logging should have failed"

        # Check that decoration still succeeded despite logging error
        assert hasattr(LoggingFailTool, "_is_tool_plugin")
        assert LoggingFailTool._is_tool_plugin is True
        assert hasattr(LoggingFailTool, "_plugin_metadata")
        assert LoggingFailTool._plugin_metadata["version"] == "1.0.0"

    except Exception as e:
        pytest.fail(f"Decorator raised an unexpected exception: {e}")

    # Verify logger.info was indeed called (and raised an exception)
    mock_logger.info.assert_called_once()
