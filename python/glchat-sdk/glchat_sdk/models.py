"""Data models for the GLChat Python client.

This module contains Pydantic models for request and response data structures
used in the GLChat Python client library.

Example:
    >>> request = MessageRequest(
    ...     chatbot_id="your-chatbot-id",
    ...     message="Hello!",
    ...     user_id="user_123"
    ... )
    >>> data = request.model_dump()

Authors:
    Vincent Chuardi (vincent.chuardi@gdplabs.id)

References:
    None
"""

from pydantic import BaseModel, ConfigDict


class MessageRequest(BaseModel):
    """Request model for sending messages to the GLChat API."""

    # Disable pydantic's protected namespace "model_"
    model_config = ConfigDict(protected_namespaces=())

    chatbot_id: str
    message: str
    parent_id: str | None = None
    source: str | None = None
    quote: str | None = None
    user_id: str | None = None
    conversation_id: str | None = None
    user_message_id: str | None = None
    assistant_message_id: str | None = None
    chat_history: str | None = None
    stream_id: str | None = None
    metadata: str | None = None
    model_name: str | None = None
    anonymize_em: bool | None = None
    anonymize_lm: bool | None = None
    use_cache: bool | None = None
    search_type: str | None = None


class PipelineRequest(BaseModel):
    """Request model for registering pipeline plugins with the GLChat API."""

    # Disable pydantic's protected namespace "model_"
    model_config = ConfigDict(protected_namespaces=())

    # Note: The zip file will be handled separately as a file upload
    # This model is for any additional metadata that might be needed
    pass
