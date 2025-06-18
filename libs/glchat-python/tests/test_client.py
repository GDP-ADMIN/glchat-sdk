"""Tests for the GLChatClient class."""

import io
from unittest.mock import Mock, patch

import pytest
from glchat_python.client import GLChatClient


@pytest.fixture
def client():
    """Create a GLChatClient instance for testing."""
    return GLChatClient(base_url="https://test-api.example.com")


@pytest.fixture
def mock_response():
    """Create a mock streaming response."""
    mock = Mock()
    mock.iter_bytes.return_value = [b"Hello", b" ", b"World"]
    mock.raise_for_status = Mock()
    return mock


def test_send_message_basic(client, mock_response):
    """Test basic message sending without files."""
    with patch("httpx.Client.stream") as mock_stream:
        mock_stream.return_value.__enter__.return_value = mock_response

        response = client.send_message(chatbot_id="test-bot", message="Hello")

        # Convert iterator to list to test all chunks
        chunks = list(response)

        assert chunks == [b"Hello", b" ", b"World"]
        mock_stream.assert_called_once()


def test_send_message_with_file_path(client, mock_response, tmp_path):
    """Test sending message with a file path."""
    # Create a temporary file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    with patch("httpx.Client.stream") as mock_stream:
        mock_stream.return_value.__enter__.return_value = mock_response

        response = client.send_message(
            chatbot_id="test-bot", message="Hello", files=[str(test_file)]
        )

        chunks = list(response)
        assert chunks == [b"Hello", b" ", b"World"]
        mock_stream.assert_called_once()


def test_send_message_with_bytes(client, mock_response):
    """Test sending message with bytes data."""
    test_bytes = b"test content"

    with patch("httpx.Client.stream") as mock_stream:
        mock_stream.return_value.__enter__.return_value = mock_response

        response = client.send_message(
            chatbot_id="test-bot", message="Hello", files=[test_bytes]
        )

        chunks = list(response)
        assert chunks == [b"Hello", b" ", b"World"]
        mock_stream.assert_called_once()


def test_send_message_with_file_object(client, mock_response):
    """Test sending message with a file-like object."""
    file_obj = io.BytesIO(b"test content")
    file_obj.name = "test.txt"

    with patch("httpx.Client.stream") as mock_stream:
        mock_stream.return_value.__enter__.return_value = mock_response

        response = client.send_message(
            chatbot_id="test-bot", message="Hello", files=[file_obj]
        )

        chunks = list(response)
        assert chunks == [b"Hello", b" ", b"World"]
        mock_stream.assert_called_once()


def test_send_message_with_invalid_file_type(client):
    """Test sending message with invalid file type."""
    with pytest.raises(ValueError, match="Unsupported file type"):
        list(
            client.send_message(
                chatbot_id="test-bot", message="Hello", files=[123]  # Invalid file type
            )
        )


def test_send_message_with_additional_params(client, mock_response):
    """Test sending message with additional parameters."""
    with patch("httpx.Client.stream") as mock_stream:
        mock_stream.return_value.__enter__.return_value = mock_response

        response = client.send_message(
            chatbot_id="test-bot",
            message="Hello",
            user_id="test-user",
            conversation_id="test-conv",
            model_name="gpt-4",
        )

        chunks = list(response)
        assert chunks == [b"Hello", b" ", b"World"]
        mock_stream.assert_called_once()
