"""Response handling for the GLChat Python client.

This module provides the MessageAPI class for handling message operations
with the GLChat backend, including streaming responses and file uploads.

Authors:
    Vincent Chuardi (vincent.chuardi@gdplabs.id)

References:
    None
"""

import logging
from collections.abc import Iterator
from pathlib import Path
from typing import Any, BinaryIO
from urllib.parse import urljoin

import httpx

from glchat_sdk.models import MessageRequest

logger = logging.getLogger(__name__)

FILE_TYPE = "application/octet-stream"


class MessageAPI:
    """Handles message API operations for the GLChat API."""

    def __init__(self, client):
        self._client = client

    def _validate_inputs(self, chatbot_id: str, message: str) -> None:
        """Validate input parameters.

        Args:
            chatbot_id (str): Chatbot identifier
            message (str): User message

        Raises:
            ValueError: If chatbot_id or message is empty
        """
        if not chatbot_id:
            raise ValueError("chatbot_id cannot be empty")
        if not message:
            raise ValueError("message cannot be empty")

    def _prepare_request_data(
        self,
        chatbot_id: str,
        message: str,
        parent_id: str | None = None,
        source: str | None = None,
        quote: str | None = None,
        user_id: str | None = None,
        conversation_id: str | None = None,
        user_message_id: str | None = None,
        assistant_message_id: str | None = None,
        chat_history: str | None = None,
        stream_id: str | None = None,
        metadata: str | None = None,
        model_name: str | None = None,
        anonymize_em: bool | None = None,
        anonymize_lm: bool | None = None,
        use_cache: bool | None = None,
        search_type: str | None = None,
    ) -> dict[str, Any]:
        """Prepare request data for the API call.

        Args:
            chatbot_id (str): Required chatbot identifier
            message (str): Required user message
            parent_id (str | None): Parent message ID for threading
            source (str | None): Source identifier for the message
            quote (str | None): Quoted message content
            user_id (str | None): User identifier
            conversation_id (str | None): Conversation identifier
            user_message_id (str | None): User message identifier
            assistant_message_id (str | None): Assistant message identifier
            chat_history (str | None): Chat history context
            stream_id (str | None): Stream identifier
            metadata (str | None): Additional metadata
            model_name (str | None): Model name to use for generation
            anonymize_em (bool | None): Whether to anonymize embeddings
            anonymize_lm (bool | None): Whether to anonymize language model
            use_cache (bool | None): Whether to use cached responses
            search_type (str | None): Type of search to perform

        Returns:
            Dict containing the prepared request data
        """
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
        return request.model_dump(exclude_none=True)

    def _prepare_headers(self) -> dict[str, str]:
        """Prepare headers for the API request.

        Returns:
            Dict containing the request headers
        """
        headers = {}
        if self._client.api_key:
            headers["Authorization"] = f"Bearer {self._client.api_key}"
        if self._client.tenant_id:
            headers["X-Tenant-ID"] = self._client.tenant_id
        return headers

    def _process_file_item(
        self, file_item: str | Path | BinaryIO | bytes
    ) -> tuple[str, tuple[str, str | BinaryIO | bytes, str]]:
        """Process a single file item and return the file tuple for httpx.

        Args:
            file_item (Union[str, Path, BinaryIO, bytes]): Item to process

        Returns:
            Tuple of (field_name, (filename, file_content, content_type))

        Raises:
            ValueError: If file type is not supported
        """
        if isinstance(file_item, str | Path):
            # File path
            file_path = Path(file_item)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            with open(file_path, "rb") as f:
                return ("files", (file_path.name, f.read(), FILE_TYPE))
        elif isinstance(file_item, bytes):
            # Raw bytes
            return ("files", ("file", file_item, FILE_TYPE))
        elif hasattr(file_item, "read"):
            # File-like object - pass directly to avoid memory issues
            filename = getattr(file_item, "name", "file")
            return ("files", (filename, file_item, FILE_TYPE))
        else:
            raise ValueError(f"Unsupported file type: {type(file_item)}")

    def _prepare_files(
        self, files: list[str | Path | BinaryIO | bytes] | None
    ) -> list[tuple[str, tuple[str, str | BinaryIO | bytes, str]]] | None:
        """Prepare files for upload.

        Args:
            files (list[Union[str, Path, BinaryIO, bytes]] | None): List of files to process

        Returns:
            List of file tuples for httpx or None if no files

        Raises:
            ValueError: If any file type is not supported
            FileNotFoundError: If any file path doesn't exist
        """
        if not files:
            return None

        files_data = []
        for file_item in files:
            try:
                file_tuple = self._process_file_item(file_item)
                files_data.append(file_tuple)
            except (ValueError, FileNotFoundError) as e:
                logger.error("Error processing file %s: %s", file_item, str(e))
                raise

        return files_data

    def _make_streaming_request(
        self,
        url: str,
        data: dict[str, Any],
        files: list[tuple[str, tuple[str, str | BinaryIO | bytes, str]]] | None,
        headers: dict[str, str],
    ) -> Iterator[bytes]:
        """Make the streaming HTTP request.

        Args:
            url (str): API endpoint URL
            data (dict[str, Any]): Request data
            files (list[Tuple[str, Tuple[str, Union[str, BinaryIO, bytes], str]]]
                | None, Optional): Prepared files data
            headers (dict[str, str]): Request headers

        Yields:
            bytes: Streaming response chunks

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        timeout = httpx.Timeout(self._client.timeout, read=self._client.timeout)

        with httpx.Client(timeout=timeout) as client:
            with client.stream(
                "POST",
                url,
                data=data,
                files=files,
                headers=headers,
            ) as response:
                response.raise_for_status()
                yield from response.iter_bytes()

    def create(
        self,
        chatbot_id: str,
        message: str,
        files: list[str | Path | BinaryIO | bytes] | None = None,
        parent_id: str | None = None,
        source: str | None = None,
        quote: str | None = None,
        user_id: str | None = None,
        conversation_id: str | None = None,
        user_message_id: str | None = None,
        assistant_message_id: str | None = None,
        chat_history: str | None = None,
        stream_id: str | None = None,
        metadata: str | None = None,
        model_name: str | None = None,
        anonymize_em: bool | None = None,
        anonymize_lm: bool | None = None,
        use_cache: bool | None = None,
        search_type: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> Iterator[bytes]:
        """
        Create a streaming response from the GLChat API.

        Args:
            chatbot_id (str): Required chatbot identifier
            message (str): Required user message
            files (list[Union[str, Path, BinaryIO, bytes]] | None): List of files
                (filepath, binary, file object, or bytes)
            parent_id (str | None): Parent message ID for threading
            source (str | None): Source identifier for the message
            quote (str | None): Quoted message content
            user_id (str | None): User identifier
            conversation_id (str | None): Conversation identifier
            user_message_id (str | None): User message identifier
            assistant_message_id (str | None): Assistant message identifier
            chat_history (str | None): Chat history context
            stream_id (str | None): Stream identifier
            metadata (str | None): Additional metadata
            model_name (str | None): Model name to use for generation
            anonymize_em (bool | None): Whether to anonymize embeddings
            anonymize_lm (bool | None): Whether to anonymize language model
            use_cache (bool | None): Whether to use cached responses
            search_type (str | None): Type of search to perform
            headers (dict[str, str] | None): Custom headers to include in the request

        Yields:
            bytes: Streaming response chunks

        Raises:
            ValueError: If input validation fails
            FileNotFoundError: If any file path doesn't exist
            httpx.HTTPStatusError: If the API request fails
        """
        # Validate inputs
        self._validate_inputs(chatbot_id, message)

        logger.debug("Sending message to chatbot %s", chatbot_id)

        # Prepare request components
        url = urljoin(self._client.base_url, "message")
        data = self._prepare_request_data(
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
        base_headers = self._prepare_headers()
        if headers:
            base_headers.update(headers)
        files_data = self._prepare_files(files)

        # Make the streaming request
        yield from self._make_streaming_request(url, data, files_data, base_headers)
