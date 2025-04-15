"""Plugin system for GLLM Agents.

This module initializes the plugin system for all agent types and provides mechanisms for dynamic
tool registration similar to VSCode extensions.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

# Re-export public API from appropriate modules
# Replace external imports with local ones
from gllm_plugin.tools.decorators import get_plugin_metadata, is_tool_plugin, tool_plugin

# For backward compatibility, provide a version in the main namespace
__all__ = [
    "tool_plugin",
    "is_tool_plugin",
    "get_plugin_metadata",
]
