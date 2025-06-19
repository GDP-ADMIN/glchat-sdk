"""Data models for the GLChat Python client."""

from pydantic import BaseModel


class MessageRequest(BaseModel):
    """Request model for sending messages to the GLChat API."""

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
