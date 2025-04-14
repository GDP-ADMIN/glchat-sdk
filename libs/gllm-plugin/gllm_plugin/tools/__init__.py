"""Plugin system for GLLM Agents.

This module initializes the plugin system for all agent types and provides mechanisms for dynamic
tool registration similar to VSCode extensions.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

# Re-export public API from appropriate modules
# Import the new decorator
from gllm_agents.plugins.decorators import (
    tool_plugin,
)
from gllm_agents.plugins.plugin import (
    AGENT_TOOL_PLUGINS,
    PLUGIN_REGISTRY,
    register_tool_plugin,
    register_tool_plugin_from_path,
)
from gllm_agents.plugins.tool_handler import (
    ToolHandler,
    get_plugin_manager,
    get_tool_handler,
    initialize_tool_plugins,
)
from gllm_agents.plugins.tool_plugin import (
    ToolPlugin,
)

# For backward compatibility, provide a version in the main namespace
__all__ = [
    "ToolPlugin",
    "ToolHandler",
    "AGENT_TOOL_PLUGINS",
    "PLUGIN_REGISTRY",
    "register_tool_plugin",
    "get_tool_handler",
    "get_plugin_manager",
    "initialize_tool_plugins",
    "register_tool_plugin_from_path",
    "tool_plugin",
]
