"""GLChat Python client library for interacting with the GLChat Backend API.

This library provides a simple interface to interact with the GLChat backend,
supporting message sending and file uploads with streaming responses.

Example:
    >>> client = GLChatClient()
    >>> for chunk in client.send_message(chatbot_id="your-chatbot-id", message="Hello!"):
    ...     print(chunk.decode("utf-8"), end="")
"""

import logging
from pathlib import Path
from typing import BinaryIO, Iterator, List, Optional, Union

import httpx

from .models import MessageRequest

FILE_TYPE = "application/octet-stream"
DEFAULT_BASE_URL = "https://stag-gbe-gdplabs-gen-ai-starter.obrol.id"

logger = logging.getLogger(__name__)


class GLChatClient:
    """GLChat Backend API Client"""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
    ):
        """
        Initialize GLChat client

        Args:
            base_url: Base URL for the GLChat API
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url if base_url else DEFAULT_BASE_URL
        self.timeout = timeout

    def _validate_inputs(self, chatbot_id: str, message: str) -> None:
        """Validate input parameters."""
        if not chatbot_id:
            raise ValueError("chatbot_id cannot be empty")
        if not message:
            raise ValueError("message cannot be empty")

    def send_message(
        self,
        chatbot_id: str,
        message: str,
        files: Optional[List[Union[str, Path, BinaryIO, bytes]]] = None,
        **kwargs,
    ) -> Iterator[bytes]:
        """
        Send a message and get streaming response

        Args:
            chatbot_id: Required chatbot identifier
            message: Required user message
            files: List of files (filepath, binary, file object, or bytes)
            **kwargs: Additional message parameters

        Yields:
            bytes: Streaming response chunks
        """
        self._validate_inputs(chatbot_id, message)

        logger.debug("Sending message to chatbot %s", chatbot_id)

        url = f"{self.base_url}/message"

        # Create message request
        request = MessageRequest(chatbot_id=chatbot_id, message=message, **kwargs)
        data = request.model_dump(exclude_none=True)

        # Prepare files
        files_data = []
        if files:
            for file_item in files:
                if isinstance(file_item, (str, Path)):
                    # File path
                    file_path = Path(file_item)
                    with open(file_path, "rb") as f:
                        files_data.append(
                            (
                                "files",
                                (file_path.name, f.read(), FILE_TYPE),
                            )
                        )
                elif isinstance(file_item, bytes):
                    # Raw bytes
                    files_data.append(("files", ("file", file_item, FILE_TYPE)))
                elif hasattr(file_item, "read"):
                    # File-like object
                    filename = getattr(file_item, "name", "file")
                    content = file_item.read()
                    files_data.append(("files", (filename, content, FILE_TYPE)))
                else:
                    raise ValueError(f"Unsupported file type: {type(file_item)}")

        with httpx.Client(
            timeout=httpx.Timeout(self.timeout, read=self.timeout)
        ) as client:
            with client.stream(
                "POST",
                url,
                data=data,
                files=files_data if files_data else None,
            ) as response:
                response.raise_for_status()
                for chunk in response.iter_bytes():
                    yield chunk
