"""Tool Plugin Decorators.

This module provides decorators for registering tool plugins using a simple decorator syntax
rather than requiring explicit inheritance from ToolPlugin class.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import inspect
from typing import Callable, Optional, Type

from langchain_core.tools import BaseTool

from gllm_agents.plugins.plugin import (
    register_tool_plugin,
)
from gllm_agents.plugins.tool_plugin import (
    ToolPlugin,
)
from gllm_agents.utils.logger import logger


def tool_plugin(
    version: str = "1.0.0",
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Callable[[Type[BaseTool]], Type[BaseTool]]:
    """Decorator to register a BaseTool class as a tool plugin.

    This decorator creates a dynamically generated ToolPlugin class
    and registers it with the plugin system. This is the standard way
    to create and register tools in the system.

    Args:
        version: Version of the plugin (defaults to "1.0.0")
        name: Optional custom name for the plugin (defaults to tool's name)
        description: Optional custom description (defaults to tool's description)

    Returns:
        A decorator function that wraps the tool class

    Example:
        ```python
        @tool_plugin(version="1.0.0")
        class MyAwesomeTool(BaseTool):
            name = "my_awesome_tool"
            description = "Does something awesome"

            def _run(self, **kwargs):
                return "Awesome result!"
        ```
    """

    def decorator(tool_class: Type[BaseTool]) -> Type[BaseTool]:
        if not inspect.isclass(tool_class) or not issubclass(tool_class, BaseTool):
            raise TypeError(f"Expected a BaseTool subclass, got {tool_class}")

        # Extract tool metadata for plugin creation using a simple approach
        tool_name = getattr(tool_class, "name", "unknown_tool")
        tool_description = getattr(tool_class, "description", "No description provided")

        # Create a dynamic ToolPlugin class
        plugin_name = name or f"{tool_name}_plugin"
        plugin_description = description or tool_description

        # Create a dynamic class that inherits from ToolPlugin
        plugin_class = type(
            f"{tool_class.__name__}Plugin",
            (ToolPlugin,),
            {
                "name": plugin_name,
                "description": plugin_description,
                "version": version,
                "create_tool": lambda self, **kwargs: tool_class(**kwargs),
                "__module__": tool_class.__module__,
                "__doc__": f"Auto-generated plugin for {tool_class.__name__}",
            },
        )

        # Register the dynamically created plugin
        register_tool_plugin(plugin_class)

        # Attach the plugin class to the tool class for reference
        tool_class._plugin_class = plugin_class

        logger.info(f"Registered tool {tool_name} as plugin {plugin_name} with version {version}")

        return tool_class

    return decorator
