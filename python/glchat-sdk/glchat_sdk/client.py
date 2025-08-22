"""GLChat Python client library for interacting with the GLChat Backend API.

This library provides a simple interface to interact with the GLChat backend,
supporting message sending and file uploads with streaming responses.

Example:
    >>> client = GLChat(api_key="your-api-key")
    >>> for chunk in client.message.create(
    ...     chatbot_id="your-chatbot-id",
    ...     message="Hello!",
    ...     parent_id="msg_123",
    ...     user_id="user_456"
    ... ):
    ...     print(chunk.decode("utf-8"), end="")

Authors:
    Vincent Chuardi (vincent.chuardi@gdplabs.id)

References:
    None
"""

import os

from glchat_sdk.conversation import ConversationAPI
from glchat_sdk.message import MessageAPI

# Ensure the URL ends with a slash; without the trailing slash, the base path will be incorrect.
DEFAULT_BASE_URL = "https://chat.gdplabs.id/api/proxy/"


class GLChat:
    """GLChat Backend API Client.

    Attributes:
        api_key: API key for authentication
        base_url: Base URL for the GLChat API
        timeout: Request timeout in seconds
        message: MessageAPI instance for message operations
        conversation: ConversationAPI instance for conversation operations
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 60.0,
        tenant_id: str | None = None,
    ):
        """
        Initialize GLChat client

        Args:
            api_key (str | None): API key for authentication. If not provided,
                will try to get from GLCHAT_API_KEY environment variable
            base_url (str | None): Base URL for the GLChat API. If not provided,
                will try to get from GLCHAT_BASE_URL environment variable,
                otherwise uses default
            timeout (float): Request timeout in seconds
            tenant_id (str | None): Tenant ID for multi-tenancy. If not provided,
                will try to get from GLCHAT_TENANT_ID environment variable
        """
        self.api_key = api_key or os.getenv("GLCHAT_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it via 'api_key' parameter or "
                "'GLCHAT_API_KEY' environment variable."
            )

        self.base_url = base_url or os.getenv("GLCHAT_BASE_URL") or DEFAULT_BASE_URL
        self.timeout = timeout
        self.tenant_id = tenant_id or os.getenv("GLCHAT_TENANT_ID")
        self.message = MessageAPI(self)
        self.conversation = ConversationAPI(self)
