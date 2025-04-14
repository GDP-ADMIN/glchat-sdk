"""Tool Handler for Agent Tool plugins.

This handler manages Tool plugins for different agent types and provides necessary services.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from typing import Any, Dict, List, Optional, Type

from bosa_core import Plugin, PluginManager
from bosa_core.plugin.handler import PluginHandler
from langchain_core.tools import BaseTool

from gllm_plugin.tools.tool_plugin import ToolPlugin
from gllm_plugin.utils.logger import logger


class ToolHandler(PluginHandler):
    """Handler for Agent Tool plugins.

    This handler manages tool plugins and provides a registry for dynamically loaded tools
    for different agent types.
    """

    def __init__(self, **config_kwargs):
        """Initialize the tool handler.

        Args:
            **config_kwargs: Configuration parameters that will be passed to tools
        """
        self.config_kwargs = config_kwargs
        self._tool_registry: Dict[str, ToolPlugin] = {}
        self._tool_instances: Dict[str, BaseTool] = {}

    @classmethod
    def create_injections(cls, instance: "ToolHandler") -> Dict[Type[Any], Any]:
        """Create injection mappings for tool plugins.

        Args:
            instance: The handler instance providing injections

        Returns:
            Dictionary mapping service types to their instances
        """
        return {}

    @classmethod
    def initialize_plugin(cls, instance: "ToolHandler", plugin: Plugin) -> None:
        """Initialize plugin-specific resources.

        This method is called after plugin creation and service injection.

        Args:
            instance: The handler instance
            plugin: The tool plugin instance
        """
        if not isinstance(plugin, ToolPlugin):
            logger.warning(f"Plugin {plugin.name} is not a ToolPlugin, skipping initialization")
            return

        # Register the tool plugin
        instance._tool_registry[plugin.name] = plugin

        # Create tool instance with any provided configuration
        config = instance.config_kwargs.copy()
        tool_instance = plugin.create_tool_instance(**config)

        # Use the tool's actual name instead of the plugin name
        tool_name = getattr(tool_instance, "name", plugin.name)
        instance._tool_instances[tool_name] = tool_instance

        # Log plugin initialization
        logger.info(f"Initialized tool plugin: {plugin.name} with tool name: {tool_name}")

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool instance by name.

        Args:
            tool_name: The name of the tool

        Returns:
            The tool instance or None if not found
        """
        return self._tool_instances.get(tool_name)

    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tool instances.

        Returns:
            List of all registered tool instances
        """
        return list(self._tool_instances.values())

    def register_tool_instance(self, tool_name: str, tool_instance: BaseTool) -> None:
        """Register a tool instance directly.

        This method allows for registering tool instances that are created outside
        of the plugin system.

        Args:
            tool_name: The name for the tool
            tool_instance: The tool instance to register
        """
        self._tool_instances[tool_name] = tool_instance
        logger.info(f"Registered external tool: {tool_name}")


def get_tool_handler() -> Optional["ToolHandler"]:
    """Get the tool handler instance.

    This function uses the PluginManager to retrieve the singleton instance
    of ToolHandler. The PluginManager ensures only one instance exists
    across the application.

    Returns:
        The tool handler instance or None if not initialized

    Example:
        ```python
        # Get the tool handler and retrieve tools
        tool_handler = get_tool_handler()
        if tool_handler:
            # Get all tools
            all_tools = tool_handler.get_all_tools()

            # Get a specific tool by name
            search_tool = tool_handler.get_tool("search")
        ```
    """
    try:
        plugin_manager = PluginManager()
        return plugin_manager.get_handler(ToolHandler)

    except Exception as e:
        logger.warning(f"Error getting tool handler from PluginManager: {e}")
        return None


def get_plugin_manager() -> Optional[PluginManager]:
    """Get the plugin manager instance.

    Returns:
        The plugin manager instance if initialized or a new instance
    """
    # PluginManager itself maintains singleton-like behavior internally
    return PluginManager()


def initialize_tool_plugins(**config_kwargs) -> ToolHandler:
    """Initialize the agent tool plugins.

    This function creates a new ToolHandler instance, registers all available tool plugins,
    and configures the PluginManager to use this handler. It should typically be called
    once during application startup.

    Args:
        **config_kwargs: Configuration parameters to pass to the tool handler and tools.
            Common parameters include:
            - pii_manager: Optional PIIManager instance for handling sensitive data
            - api_keys: Optional dictionary of API keys for external services

    Returns:
        ToolHandler: The initialized tool handler with all registered plugins

    Example:
        ```python
        # Initialize with no special configuration
        tool_handler = initialize_tool_plugins()
        ```
    """
    # Import the plugin registry from local module
    from gllm_plugin.tools.plugin import AGENT_TOOL_PLUGINS

    # Create the tool handler without PII manager for simpler implementation
    tool_handler = ToolHandler(**config_kwargs)

    # Create the plugin manager with the tool handler
    # This updates the singleton instance of PluginManager
    plugin_manager = PluginManager(handlers=[tool_handler])

    # Register all plugins
    for plugin_class in AGENT_TOOL_PLUGINS:
        try:
            plugin_manager.register_plugin(plugin_class)
            logger.info(f"Registered agent tool plugin: {plugin_class.__name__}")
        except Exception as e:
            logger.error(f"Failed to register plugin {plugin_class.__name__}: {e}")

    return tool_handler
