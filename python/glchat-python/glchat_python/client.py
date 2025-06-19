"""GLChat Python client library for interacting with the GLChat Backend API.

This library provides a simple interface to interact with the GLChat backend,
supporting message sending and file uploads with streaming responses.

Example:
    >>> client = GLChatClient(api_key="your-api-key")
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

from glchat_python.message import MessageAPI

# Ensure the URL ends with a slash; without the trailing slash, the base path will be incorrect.
DEFAULT_BASE_URL = "https://stag-chat-ui-gdplabs-gen-ai-starter.obrol.id/api/proxy/"


class GLChatClient:
    """GLChat Backend API Client.

    Attributes:
        api_key: API key for authentication
        base_url: Base URL for the GLChat API
        timeout: Request timeout in seconds
        message: MessageAPI instance for message operations
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 60.0,
    ):
        """
        Initialize GLChat client

        Args:
            api_key (str | None): API key for authentication
            base_url [str | None]: Base URL for the GLChat API
            timeout [float]: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url if base_url else DEFAULT_BASE_URL
        self.timeout = timeout
        self.message = MessageAPI(self)
