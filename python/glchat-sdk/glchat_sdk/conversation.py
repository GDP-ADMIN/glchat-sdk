"""Conversation handling for the GLChat Python client.

This module provides the ConversationAPI class for handling conversation operations
with the GLChat backend, including creating new conversations.

Authors:
    Hermes Vincentius Gani (hermes.v.gani@gdplabs.id)

References:
    None
"""

import logging
from typing import Any
from urllib.parse import urljoin

import httpx

from glchat_sdk.models import ConversationRequest

logger = logging.getLogger(__name__)


class ConversationAPI:
    """Handles conversation API operations for the GLChat API."""

    def __init__(self, client):
        self._client = client

    def _validate_inputs(self, user_id: str, chatbot_id: str) -> None:
        """Validate input parameters.

        Args:
            user_id (str): User identifier
            chatbot_id (str): Chatbot identifier

        Raises:
            ValueError: If user_id or chatbot_id is empty
        """
        if not user_id:
            raise ValueError("user_id cannot be empty")
        if not chatbot_id:
            raise ValueError("chatbot_id cannot be empty")

    def _prepare_request_data(
        self,
        user_id: str,
        chatbot_id: str,
        title: str | None = None,
        model_name: str | None = None,
    ) -> dict[str, Any]:
        """Prepare request data for the API call.

        Args:
            user_id (str): Required user identifier
            chatbot_id (str): Required chatbot identifier
            title (str | None): Optional conversation title
            model_name (str | None): Optional model name to use

        Returns:
            dict[str, Any]: Dictionary containing the prepared request data
        """
        request = ConversationRequest(
            user_id=user_id,
            chatbot_id=chatbot_id,
            title=title,
            model_name=model_name,
        )
        return request.model_dump(exclude_none=True)

    def _prepare_headers(self) -> dict[str, str]:
        """Prepare headers for the API request.

        Returns:
            dict[str, str]: Dictionary containing the request headers
        """
        headers = {}
        if self._client.api_key:
            headers["Authorization"] = f"Bearer {self._client.api_key}"
        if self._client.tenant_id:
            headers["X-Tenant-ID"] = self._client.tenant_id
        return headers

    def create(
        self,
        user_id: str,
        chatbot_id: str,
        title: str | None = None,
        model_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Create a new conversation with the GLChat API.

        Args:
            user_id (str): Required user identifier
            chatbot_id (str): Required chatbot identifier
            title (str | None): Optional conversation title
            model_name (str | None): Optional model name to use

        Returns:
            dict[str, Any]: Dictionary containing the conversation response data

        Raises:
            ValueError: If input validation fails
            httpx.HTTPStatusError: If the API request fails
        """
        # Validate inputs
        self._validate_inputs(user_id, chatbot_id)

        logger.debug("Creating conversation for user %s with chatbot %s", user_id, chatbot_id)

        # Prepare request components
        url = urljoin(self._client.base_url, "conversations")
        data = self._prepare_request_data(
            user_id=user_id,
            chatbot_id=chatbot_id,
            title=title,
            model_name=model_name,
        )
        headers = self._prepare_headers()

        # Make the request
        timeout = httpx.Timeout(self._client.timeout)

        # Log the request details for debugging
        logger.debug("Request URL: %s", url)
        logger.debug("Request data: %s", data)
        logger.debug("Request headers: %s", headers)

        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, data=data, headers=headers)
            response.raise_for_status()
            return response.json()
