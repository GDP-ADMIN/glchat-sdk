"""Response handling for the GLChat Python client."""

import logging
from pathlib import Path
from typing import BinaryIO, Iterator, List, Optional, Union

import httpx

from .models import MessageRequest

logger = logging.getLogger(__name__)

FILE_TYPE = "application/octet-stream"


class Responses:
    """Handles response creation for the GLChat API."""

    def __init__(self, client):
        self._client = client

    def _validate_inputs(self, chatbot_id: str, message: str) -> None:
        """Validate input parameters."""
        if not chatbot_id:
            raise ValueError("chatbot_id cannot be empty")
        if not message:
            raise ValueError("message cannot be empty")

    def create(
        self,
        chatbot_id: str,
        message: str,
        files: Optional[List[Union[str, Path, BinaryIO, bytes]]] = None,
        parent_id: Optional[str] = None,
        source: Optional[str] = None,
        quote: Optional[str] = None,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        user_message_id: Optional[str] = None,
        assistant_message_id: Optional[str] = None,
        chat_history: Optional[str] = None,
        stream_id: Optional[str] = None,
        metadata: Optional[str] = None,
        model_name: Optional[str] = None,
        anonymize_em: Optional[bool] = None,
        anonymize_lm: Optional[bool] = None,
        use_cache: Optional[bool] = None,
        search_type: Optional[str] = None,
    ) -> Iterator[bytes]:
        """
        Create a streaming response from the GLChat API.

        Args:
            chatbot_id: Required chatbot identifier
            message: Required user message
            files: List of files (filepath, binary, file object, or bytes)
            parent_id: Parent message ID for threading
            source: Source identifier for the message
            quote: Quoted message content
            user_id: User identifier
            conversation_id: Conversation identifier
            user_message_id: User message identifier
            assistant_message_id: Assistant message identifier
            chat_history: Chat history context
            stream_id: Stream identifier
            metadata: Additional metadata
            model_name: Model name to use for generation
            anonymize_em: Whether to anonymize embeddings
            anonymize_lm: Whether to anonymize language model
            use_cache: Whether to use cached responses
            search_type: Type of search to perform

        Yields:
            bytes: Streaming response chunks
        """
        self._validate_inputs(chatbot_id, message)

        logger.debug("Sending message to chatbot %s", chatbot_id)

        url = f"{self._client.base_url}/message"

        # Create message request with all explicit parameters
        request = MessageRequest(
            chatbot_id=chatbot_id,
            message=message,
            parent_id=parent_id,
            source=source,
            quote=quote,
            user_id=user_id,
            conversation_id=conversation_id,
            user_message_id=user_message_id,
            assistant_message_id=assistant_message_id,
            chat_history=chat_history,
            stream_id=stream_id,
            metadata=metadata,
            model_name=model_name,
            anonymize_em=anonymize_em,
            anonymize_lm=anonymize_lm,
            use_cache=use_cache,
            search_type=search_type,
        )
        data = request.model_dump(exclude_none=True)

        # Prepare headers with API key if provided
        headers = {}
        if self._client.api_key:
            headers["Authorization"] = f"Bearer {self._client.api_key}"

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
                    # File-like object - pass directly to avoid memory issues
                    filename = getattr(file_item, "name", "file")
                    files_data.append(("files", (filename, file_item, FILE_TYPE)))
                else:
                    raise ValueError(f"Unsupported file type: {type(file_item)}")

        with httpx.Client(
            timeout=httpx.Timeout(self._client.timeout, read=self._client.timeout)
        ) as client:
            with client.stream(
                "POST",
                url,
                data=data,
                files=files_data if files_data else None,
                headers=headers,
            ) as response:
                response.raise_for_status()
                for chunk in response.iter_bytes():
                    yield chunk
