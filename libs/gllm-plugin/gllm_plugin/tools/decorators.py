"""Tool Plugin Decorators for External Use.

This module provides a standalone decorator for registering tool plugins using a simple decorator syntax
without requiring direct dependencies on the core plugin system.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
    Christian Trisno Sen Long Chen (christian.t.s.l.chen@gdplabs.id)
"""

import inspect
from typing import Any, Callable, Dict, Type

from langchain_core.tools import BaseTool

from gllm_plugin.utils import logger


def tool_plugin(
    version: str = "1.0.0",
) -> Callable[[Type[BaseTool]], Type[BaseTool]]:
    """Decorator to mark a BaseTool class as a tool plugin.

    This decorator adds metadata to the tool class that will be used by the
    plugin system when the tool is loaded. It doesn't directly register
    the tool with any system, allowing for use in external repositories.
    The actual tool name and description are intended to be retrieved
    from the tool instance at runtime.

    Args:
        version: Version of the plugin (defaults to "1.0.0")

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
        """Decorator for BaseTool classes to register them as plugins.

        Args:
            tool_class: The BaseTool class to decorate

        Returns:
            The decorated BaseTool class with plugin metadata
        """
        if not issubclass(tool_class, BaseTool):
            raise TypeError(f"{tool_class.__name__} is not a subclass of BaseTool")

        # Store basic plugin metadata as class attributes for later registration
        tool_class._plugin_metadata = {
            "version": version,
            "tool_class": tool_class.__name__,
            "module": tool_class.__module__,
        }

        # Mark the class as a decorated tool plugin for easy discovery
        tool_class._is_tool_plugin = True

        # Log the preparation (but don't require any specific logger)
        try:
            # Simplified logging message
            logger.info(f"Marked tool class {tool_class.__name__} as plugin with version {version}")
        except Exception:
            # Ignore logging errors in standalone mode
            pass

        return tool_class

    return decorator


def is_tool_plugin(obj: Any) -> bool:
    """Check if an object is a tool plugin.

    Args:
        obj: The object to check

    Returns:
        True if the object is a decorated tool plugin, False otherwise
    """
    return inspect.isclass(obj) and getattr(obj, "_is_tool_plugin", False) is True


def get_plugin_metadata(tool_class: Type[BaseTool]) -> Dict[str, Any]:
    """Get the plugin metadata from a decorated tool class.

    Args:
        tool_class: The tool class to get metadata from

    Returns:
        A dictionary of plugin metadata

    Raises:
        ValueError: If the tool class is not a decorated tool plugin
    """
    if not is_tool_plugin(tool_class):
        raise ValueError(f"{tool_class.__name__} is not a decorated tool plugin")

    return getattr(tool_class, "_plugin_metadata", {})
