"""Base Tool Plugin.

This module defines the base class for Agent Tool plugins that can be registered dynamically.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from abc import ABC, abstractmethod
from typing import Any, Type

from bosa_core.plugin.handler import PluginHandler
from bosa_core.plugin.plugin import Plugin
from langchain_core.tools import BaseTool


@Plugin.for_handler(PluginHandler)
class ToolPlugin(Plugin, ABC):
    """Base class for Tool plugins.

    This class combines the Plugin architecture with the Tool functionality,
    allowing tools to be dynamically registered at runtime for any agent type.

    To create a new tool plugin:
    1. Subclass ToolPlugin
    2. Override the create_tool() method to return your tool instance
    3. Set the name, description, and agent_type class variables

    Example:
        ```python
        class MyToolPlugin(ToolPlugin):
            name = "my_awesome_tool_plugin"
            description = "A plugin that provides an awesome tool"

            def create_tool(self, **kwargs):
                # Create and return your tool instance
                return MyAwesomeTool(**kwargs)
        ```
    """

    name: str
    description: str = "Agent tool plugin"
    version: str = "0.0.0"

    @abstractmethod
    def create_tool(self, **kwargs: Any) -> BaseTool:
        """Create a tool instance with appropriate configuration.

        This is the main method you need to implement when creating a new tool plugin.
        Simply create and return your tool instance with any needed configuration.

        Args:
            **kwargs: Configuration parameters for the tool.

        Returns:
            BaseTool: An instantiated tool ready for use.
        """
        pass

    def get_tool_class(self) -> Type[BaseTool]:
        """Get the tool class.

        Note: This is maintained for backward compatibility.
        New plugins should focus on implementing create_tool() instead.

        Returns:
            Type[BaseTool]: The tool class that will be instantiated.
        """
        # Default implementation that works in most cases
        # Can be overridden if needed
        tool = self.create_tool()
        return tool.__class__

    def create_tool_instance(self, **kwargs: Any) -> BaseTool:
        """Create a tool instance with appropriate configuration.

        Note: This is maintained for backward compatibility.
        It simply calls the new create_tool() method.

        Args:
            **kwargs: Configuration parameters for the tool.

        Returns:
            BaseTool: An instantiated tool ready for use.
        """
        return self.create_tool(**kwargs)

    @staticmethod
    def get_handler_type() -> Type:
        """Return the handler type for this plugin.

        This method is required by the plugin system.
        The PluginManager expects this to return a class type that can be used with issubclass().

        Returns:
            Type: The PluginHandler class that this plugin is designed to work with
        """
        return PluginHandler
