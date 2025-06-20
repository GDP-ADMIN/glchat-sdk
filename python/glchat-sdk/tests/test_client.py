"""Tests for the GLChat class.

Authors:
    Vincent Chuardi (vincent.chuardi@gdplabs.id)

References:
    None
"""

import io
from unittest.mock import Mock, patch

import pytest
from glchat_sdk.client import GLChat


@pytest.fixture
def client():
    """Create a GLChat instance for testing."""
    return GLChat(base_url="https://test-api.example.com")


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

        response = client.message.create(chatbot_id="test-bot", message="Hello")

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

        response = client.message.create(
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

        response = client.message.create(
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

        response = client.message.create(
            chatbot_id="test-bot", message="Hello", files=[file_obj]
        )

        chunks = list(response)
        assert chunks == [b"Hello", b" ", b"World"]
        mock_stream.assert_called_once()


def test_send_message_with_invalid_file_type(client):
    """Test sending message with invalid file type."""
    with pytest.raises(ValueError, match="Unsupported file type"):
        list(
            client.message.create(
                chatbot_id="test-bot", message="Hello", files=[123]  # Invalid file type
            )
        )


def test_send_message_with_additional_params(client, mock_response):
    """Test sending message with additional parameters."""
    with patch("httpx.Client.stream") as mock_stream:
        mock_stream.return_value.__enter__.return_value = mock_response

        response = client.message.create(
            chatbot_id="test-bot",
            message="Hello",
            user_id="test-user",
            conversation_id="test-conv",
            model_name="gpt-4",
        )

        chunks = list(response)
        assert chunks == [b"Hello", b" ", b"World"]
        mock_stream.assert_called_once()


def test_client_with_environment_variables():
    """Test client initialization with environment variables."""
    with patch.dict(
        "os.environ",
        {
            "GLCHAT_API_KEY": "test-api-key",
            "GLCHAT_BASE_URL": "https://env-test.example.com/api/",
        },
    ):
        client = GLChat()
        assert client.api_key == "test-api-key"
        assert client.base_url == "https://env-test.example.com/api/"


def test_client_environment_variables_priority():
    """Test that explicit parameters take priority over environment variables."""
    with patch.dict(
        "os.environ",
        {
            "GLCHAT_API_KEY": "env-api-key",
            "GLCHAT_BASE_URL": "https://env-test.example.com/api/",
        },
    ):
        client = GLChat(
            api_key="explicit-api-key",
            base_url="https://explicit-test.example.com/api/",
        )
        assert client.api_key == "explicit-api-key"
        assert client.base_url == "https://explicit-test.example.com/api/"


def test_client_default_base_url():
    """Test that default base URL is used when no environment variable is set."""
    with patch.dict("os.environ", {}, clear=True):
        client = GLChat()
        assert client.base_url == "https://chat.gdplabs.id/api/proxy/"
