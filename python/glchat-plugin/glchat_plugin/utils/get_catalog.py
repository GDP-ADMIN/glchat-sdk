"""Get Catalog.

Authors:
    Ryan Ignatius Hadiwijaya (ryan.i.hadiwijaya@gdplabs.id)

References:
    None
"""

from typing import Any

from gllm_inference.catalog.catalog import BaseCatalog
from gllm_inference.prompt_builder.prompt_builder import PromptBuilder
from gllm_inference.request_processor import LMRequestProcessor

DEFAULT_SCOPE = ""


def get_catalog(
    catalogs: dict[str, BaseCatalog[Any]], identifier: str, scope: str = DEFAULT_SCOPE
) -> PromptBuilder | LMRequestProcessor:
    """Get the catalog from the catalog based on the scope.

    Args:
        catalogs (dict[str, BaseCatalog[Any]]): The catalogs to search in.
        identifier (str): The identifier of the catalog.
        scope (str, optional): The catalog scope. Defaults to DEFAULT_SCOPE.

    Returns:
        PromptBuilder | LMRequestProcessor: The catalog.

    Raises:
        ValueError: If the identifier is not found in any catalog.
    """
    return _get_by_scope(catalogs, identifier, scope)


def _get_by_scope(
    catalogs: dict[str, BaseCatalog[Any]], identifier: str, scope: str = DEFAULT_SCOPE
) -> PromptBuilder | LMRequestProcessor:
    """Get the catalog based on the scope.

    The scope could be a model name (eg: openai/gpt-4o-mini), a provider name (eg: openai), or an empty string.

    This function will do the following:
    - If the exact scope is found in catalogs, and identifier is in the scope's catalog, return the catalog.
    - Otherwise, it will extract the provider name from the scope, and try to find again in the catalogs.
    - If still not found, it will try to find the catalog in the default catalog (denoted by empty string).
    - It will raise ValueError if the identifier is not found in any catalog.

    Args:
        catalogs (dict[str, BaseCatalog[Any]]): The catalogs to search in.
        identifier (str): The identifier of the catalog.
        scope (str, optional): The catalog scope. Defaults to DEFAULT_SCOPE.

    Returns:
        PromptBuilder | LMRequestProcessor: The catalog.

    Raises:
        ValueError: If the identifier is not found in any catalog.
    """
    builder = _get_from_catalogs(catalogs, identifier, scope)

    if builder is None and "/" in scope:
        builder = _get_from_catalogs(catalogs, identifier, scope.split("/", 1)[0])

    if builder is None:
        builder = _get_from_catalogs(catalogs, identifier, DEFAULT_SCOPE)

    if builder is None:
        raise ValueError(f"Catalog `{identifier}` not found in any catalog.")

    return builder


def _get_from_catalogs(
    catalogs: dict[str, BaseCatalog[Any]], identifier: str, scope: str = DEFAULT_SCOPE
) -> PromptBuilder | LMRequestProcessor | None:
    """Get the prompt builder or LM Request Processor for the scope.

    Args:
        catalogs (dict[str, BaseCatalog[Any]]): The catalogs.
        identifier (str): The identifier of the catalog.
        scope (str, optional): The scope. Defaults to DEFAULT_SCOPE.

    Returns:
        PromptBuilder | LMRequestProcessor | None: The catalog, or None if not found.
    """
    if scope in catalogs and identifier in catalogs[scope].components:
        return catalogs[scope].components[identifier]
    return None
