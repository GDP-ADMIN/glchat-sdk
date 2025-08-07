"""Get LM Invoker.

Authors:
    Ryan Ignatius Hadiwijaya (ryan.i.hadiwijaya@gdplabs.id)

References:
    None
"""

import os
from typing import Any

from gllm_core.utils.retry import RetryConfig
from gllm_inference.builder import build_lm_invoker
from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker

from glchat_plugin.constants.constants import (
    LM_INVOKER_MAX_RETRIES,
    LM_INVOKER_TIMEOUT_SECONDS,
)


def get_lm_invoker(
    provider_model_name: str, model_kwargs: dict[str, Any], model_env_kwargs: dict[str, Any]
) -> BaseLMInvoker:
    """Build the LM invoker based on the model name, model kwargs, and model env kwargs.

    Args:
        provider_model_name (str): The provider model name.
        model_kwargs (dict[str, Any]): The model kwargs.
        model_env_kwargs (dict[str, Any]): The model environment kwargs.

    Returns:
        BaseLMInvoker: The LM invoker.
    """
    lm_invoker_type = model_kwargs.get("lm_invoker_type")
    if not lm_invoker_type:
        raise ValueError("lm_invoker_type is required")

    _, model_name = provider_model_name.split("/", 1)
    model_id = f"{lm_invoker_type}/{model_name}"

    config = {
        "retry_config": RetryConfig(timeout=LM_INVOKER_TIMEOUT_SECONDS, max_retries=LM_INVOKER_MAX_RETRIES),
    }
    default_hyperparameters = model_kwargs.get("default_hyperparameters", {})
    if default_hyperparameters:
        config["default_hyperparameters"] = default_hyperparameters

    credentials = get_credentials(model_kwargs, model_env_kwargs)

    if lm_invoker_type == "azure-openai":
        azure_endpoint = _get_value_from_kwargs(model_kwargs, model_env_kwargs, "azure_endpoint")
        azure_deployment = _get_value_from_kwargs(model_kwargs, model_env_kwargs, "azure_deployment")
        if not azure_endpoint or not azure_deployment:
            raise ValueError("azure_endpoint and azure_deployment are required for azure-openai lm invoker")
        model_id = f"{lm_invoker_type}/{azure_endpoint}:{azure_deployment}"
        azure_api_version = _get_value_from_kwargs(model_kwargs, model_env_kwargs, "api_version")
        if azure_api_version:
            config["api_version"] = azure_api_version
    elif lm_invoker_type == "openai-compatible":
        base_url = _get_value_from_kwargs(model_kwargs, model_env_kwargs, "base_url")
        if not base_url:
            raise ValueError("base_url is required for openai-compatible lm invoker")
        model_id = f"{lm_invoker_type}/{base_url}:{model_name}"
    elif lm_invoker_type == "langchain":
        model_class = _get_value_from_kwargs(model_kwargs, model_env_kwargs, "model_class")
        if not model_class:
            raise ValueError("model_class is required for langchain lm invoker")
        model_id = f"{lm_invoker_type}/{model_class}:{model_name}"

    return build_lm_invoker(model_id, credentials, config)


def get_credentials(model_kwargs: dict[str, Any], model_env_kwargs: dict[str, Any]) -> Any:
    """Get the credentials for the given provider.

    Args:
        model_kwargs (dict[str, Any]): The model kwargs.
        model_env_kwargs (dict[str, Any]): The model environment kwargs.

    Returns:
        Any: The credentials.
    """
    credentials = _get_value_from_kwargs(
        model_kwargs, model_env_kwargs, "credentials"
    ) or _get_object_from_kwargs_parts(model_kwargs, model_env_kwargs, "credentials.")
    return credentials


def _get_value_from_kwargs(model_kwargs: dict[str, Any], model_env_kwargs: dict[str, Any], key: str) -> Any:
    """Get value from model environment kwargs.

    Args:
        model_kwargs (dict[str, Any]): The model kwargs.
        model_env_kwargs (dict[str, Any]): The model environment kwargs.
        key (str): The key.

    Returns:
        Any: The value.
    """
    value = model_kwargs.get(key)
    if value:
        return value
    value = model_env_kwargs.get(key)
    if value:
        env_value = os.getenv(value)
        if not env_value:
            raise ValueError(f"Environment variable {value} is not set")
        return env_value
    return None


def _get_object_from_kwargs_parts(model_kwargs: dict[str, Any], model_env_kwargs: dict[str, Any], prefix: str) -> Any:
    """Get object from model environment kwargs.

    Args:
        model_kwargs (dict[str, Any]): The model kwargs.
        model_env_kwargs (dict[str, Any]): The model environment kwargs.
        prefix (str): The prefix.

    Returns:
        Any: The value.
    """
    result = {}
    for key in model_kwargs:
        if key.startswith(prefix):
            result[key[len(prefix) :]] = _get_value_from_kwargs(model_kwargs, model_env_kwargs, key)

    for key in model_env_kwargs:
        if key.startswith(prefix):
            result[key[len(prefix) :]] = _get_value_from_kwargs(model_kwargs, model_env_kwargs, key)

    return result
