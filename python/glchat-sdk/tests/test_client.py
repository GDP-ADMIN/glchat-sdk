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
    return GLChat(
        api_key="test_api_key", base_url="https://test-api.example.com", tenant_id="test_tenant"
    )


@pytest.fixture
def mock_response():
    """Create a mock streaming response."""
    mock = Mock()
    mock.iter_bytes.return_value = [b"Hello", b" ", b"World"]
    mock.raise_for_status = Mock()
    return mock


def test_send_message_basic(client, mock_response):
    """Test basic message sending without files.

    Condition:
        - Client is initialized with valid API key and base URL
        - Message is sent without file attachments
        - Mock streaming response is configured

    Expected:
        - Response should be an iterator yielding bytes chunks
        - Chunks should match the mock response data
        - HTTP stream should be called exactly once
    """
    with patch("httpx.Client.stream") as mock_stream:
        mock_stream.return_value.__enter__.return_value = mock_response

        response = client.message.create(chatbot_id="test-bot", message="Hello")

        # Convert iterator to list to test all chunks
        chunks = list(response)

        assert chunks == [b"Hello", b" ", b"World"]
        mock_stream.assert_called_once()


def test_send_message_with_file_path(client, mock_response, tmp_path):
    """Test sending message with a file path.

    Condition:
        - Client is initialized with valid API key and base URL
        - Temporary file is created with test content
        - Message is sent with file path attachment
        - Mock streaming response is configured

    Expected:
        - Response should be an iterator yielding bytes chunks
        - Chunks should match the mock response data
        - HTTP stream should be called exactly once
        - File should be processed correctly
    """
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
    """Test sending message with bytes data.

    Condition:
        - Client is initialized with valid API key and base URL
        - Message is sent with bytes data attachment
        - Mock streaming response is configured

    Expected:
        - Response should be an iterator yielding bytes chunks
        - Chunks should match the mock response data
        - HTTP stream should be called exactly once
        - Bytes data should be processed correctly
    """
    test_bytes = b"test content"

    with patch("httpx.Client.stream") as mock_stream:
        mock_stream.return_value.__enter__.return_value = mock_response

        response = client.message.create(chatbot_id="test-bot", message="Hello", files=[test_bytes])

        chunks = list(response)
        assert chunks == [b"Hello", b" ", b"World"]
        mock_stream.assert_called_once()


def test_send_message_with_file_object(client, mock_response):
    """Test sending message with a file-like object.

    Condition:
        - Client is initialized with valid API key and base URL
        - Message is sent with file-like object attachment
        - Mock streaming response is configured

    Expected:
        - Response should be an iterator yielding bytes chunks
        - Chunks should match the mock response data
        - HTTP stream should be called exactly once
        - File-like object should be processed correctly
    """
    file_obj = io.BytesIO(b"test content")
    file_obj.name = "test.txt"

    with patch("httpx.Client.stream") as mock_stream:
        mock_stream.return_value.__enter__.return_value = mock_response

        response = client.message.create(chatbot_id="test-bot", message="Hello", files=[file_obj])

        chunks = list(response)
        assert chunks == [b"Hello", b" ", b"World"]
        mock_stream.assert_called_once()


def test_send_message_with_invalid_file_type(client):
    """Test sending message with invalid file type.

    Condition:
        - Client is initialized with valid API key and base URL
        - Message is sent with unsupported file type (integer)

    Expected:
        - ValueError should be raised with "Unsupported file type" message
        - API call should fail before making HTTP request
    """
    with pytest.raises(ValueError, match="Unsupported file type"):
        list(
            client.message.create(
                chatbot_id="test-bot",
                message="Hello",
                files=[123],  # Invalid file type
            )
        )


def test_send_message_with_additional_params(client, mock_response):
    """Test sending message with additional parameters.

    Condition:
        - Client is initialized with valid API key and base URL
        - Message is sent with additional parameters (user_id, conversation_id, model_name)
        - Mock streaming response is configured

    Expected:
        - Response should be an iterator yielding bytes chunks
        - Chunks should match the mock response data
        - HTTP stream should be called exactly once
        - Additional parameters should be included in the request
    """
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


def test_send_message_includes_tenant_id_header(client, mock_response):
    """Test that tenant_id header is included in message requests.

    Condition:
        - Client is initialized with valid API key, base URL, and tenant_id
        - Message is sent to trigger HTTP request
        - Mock streaming response is configured

    Expected:
        - X-Tenant-ID header should be included in the request headers
        - Header value should match the client's tenant_id
        - HTTP stream should be called exactly once
    """
    with patch("httpx.Client.stream") as mock_stream:
        mock_stream.return_value.__enter__.return_value = mock_response

        response = client.message.create(chatbot_id="test-bot", message="Hello")

        # Convert iterator to list to consume the response
        list(response)

        # Check that the tenant_id header was included
        mock_stream.assert_called_once()
        call_args = mock_stream.call_args
        headers = call_args[1].get("headers", {})
        assert "X-Tenant-ID" in headers
        assert headers["X-Tenant-ID"] == "test_tenant"


def test_client_with_environment_variables():
    """Test client initialization with environment variables.

    Condition:
        - GLCHAT_API_KEY and GLCHAT_BASE_URL environment variables are set
        - Client is initialized without explicit parameters

    Expected:
        - Client should use API key from GLCHAT_API_KEY environment variable
        - Client should use base URL from GLCHAT_BASE_URL environment variable
    """
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
    """Test that explicit parameters take priority over environment variables.

    Condition:
        - GLCHAT_API_KEY and GLCHAT_BASE_URL environment variables are set
        - Client is initialized with explicit parameters

    Expected:
        - Explicit API key should take priority over GLCHAT_API_KEY environment variable
        - Explicit base URL should take priority over GLCHAT_BASE_URL environment variable
    """
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
    """Test that default base URL is used when no environment variable is set.

    Condition:
        - No environment variables are set
        - Client is initialized with only API key

    Expected:
        - Client should use the default base URL from the code
        - Default base URL should be "https://chat.gdplabs.id/api/proxy/"
    """
    with patch.dict("os.environ", {}, clear=True):
        client = GLChat(api_key="test_api_key")
        assert client.base_url == "https://chat.gdplabs.id/api/proxy/"


def test_client_tenant_id_environment_variable():
    """Test client initialization with tenant_id from environment variable.

    Condition:
        - GLCHAT_API_KEY and GLCHAT_TENANT_ID environment variables are set
        - Client is initialized without explicit tenant_id parameter

    Expected:
        - Client should use tenant_id from GLCHAT_TENANT_ID environment variable
        - Client should use API key from GLCHAT_API_KEY environment variable
    """
    with patch.dict(
        "os.environ",
        {
            "GLCHAT_API_KEY": "test-api-key",
            "GLCHAT_TENANT_ID": "env-tenant-id",
        },
    ):
        client = GLChat()
        assert client.tenant_id == "env-tenant-id"


def test_client_tenant_id_parameter_priority():
    """Test that explicit tenant_id parameter takes priority over environment variable.

    Condition:
        - GLCHAT_API_KEY and GLCHAT_TENANT_ID environment variables are set
        - Client is initialized with explicit tenant_id parameter

    Expected:
        - Explicit tenant_id should take priority over GLCHAT_TENANT_ID environment variable
        - Client should use the explicit tenant_id value
    """
    with patch.dict(
        "os.environ",
        {
            "GLCHAT_API_KEY": "test-api-key",
            "GLCHAT_TENANT_ID": "env-tenant-id",
        },
    ):
        client = GLChat(tenant_id="explicit-tenant-id")
        assert client.tenant_id == "explicit-tenant-id"
