"""Tests for the ConversationAPI class.

Authors:
    Vincent Chuardi (vincent.chuardi@gdplabs.id)

References:
    None
"""

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
    """Create a mock response."""
    mock = Mock()
    mock.json.return_value = {
        "conversation_id": "conv_123",
        "user_id": "user_456",
        "chatbot_id": "bot_789",
        "title": "Test Conversation",
        "model_name": "gpt-4",
    }
    mock.raise_for_status = Mock()
    return mock


def test_create_conversation_basic(client, mock_response):
    """Test basic conversation creation.

    Condition:
        - Client is initialized with valid API key, base URL, and tenant_id
        - Mock response is configured with conversation data
        - Basic conversation creation is called with user_id and chatbot_id

    Expected:
        - Response should contain the expected conversation data
        - HTTP POST should be called exactly once
        - Data should be sent as form data, not JSON
    """
    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = mock_response

        response = client.conversation.create(user_id="user_456", chatbot_id="bot_789")

        assert response["conversation_id"] == "conv_123"
        assert response["user_id"] == "user_456"
        assert response["chatbot_id"] == "bot_789"
        mock_post.assert_called_once()

        # Check that data is sent as form data, not JSON
        call_args = mock_post.call_args
        assert "data" in call_args[1]
        assert "json" not in call_args[1]


def test_create_conversation_with_title(client, mock_response):
    """Test conversation creation with title.

    Condition:
        - Client is initialized with valid API key, base URL, and tenant_id
        - Mock response is configured with conversation data
        - Conversation creation is called with user_id, chatbot_id, and title

    Expected:
        - Response should contain the expected title
        - HTTP POST should be called exactly once
        - Data should be sent as form data, not JSON
    """
    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = mock_response

        response = client.conversation.create(
            user_id="user_456", chatbot_id="bot_789", title="My Test Conversation"
        )

        assert response["title"] == "Test Conversation"
        mock_post.assert_called_once()

        # Check that data is sent as form data, not JSON
        call_args = mock_post.call_args
        assert "data" in call_args[1]
        assert "json" not in call_args[1]


def test_create_conversation_with_model(client, mock_response):
    """Test conversation creation with model name.

    Condition:
        - Client is initialized with valid API key, base URL, and tenant_id
        - Mock response is configured with conversation data
        - Conversation creation is called with user_id, chatbot_id, and model_name

    Expected:
        - Response should contain the expected model_name
        - HTTP POST should be called exactly once
        - Data should be sent as form data, not JSON
    """
    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = mock_response

        response = client.conversation.create(
            user_id="user_456", chatbot_id="bot_789", model_name="gpt-4"
        )

        assert response["model_name"] == "gpt-4"
        mock_post.assert_called_once()

        # Check that data is sent as form data, not JSON
        call_args = mock_post.call_args
        assert "data" in call_args[1]
        assert "json" not in call_args[1]


def test_create_conversation_with_all_params(client, mock_response):
    """Test conversation creation with all parameters.

    Condition:
        - Client is initialized with valid API key, base URL, and tenant_id
        - Mock response is configured with conversation data
        - Conversation creation is called with all optional parameters

    Expected:
        - Response should contain all expected conversation data
        - HTTP POST should be called exactly once
        - Data should be sent as form data, not JSON
    """
    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = mock_response

        response = client.conversation.create(
            user_id="user_456",
            chatbot_id="bot_789",
            title="My Test Conversation",
            model_name="gpt-4",
        )

        assert response["conversation_id"] == "conv_123"
        assert response["title"] == "Test Conversation"  # Mock response returns "Test Conversation"
        assert response["model_name"] == "gpt-4"
        mock_post.assert_called_once()

        # Check that data is sent as form data, not JSON
        call_args = mock_post.call_args
        assert "data" in call_args[1]
        assert "json" not in call_args[1]


def test_create_conversation_missing_user_id(client):
    """Test conversation creation with missing user_id.

    Condition:
        - Client is initialized with valid API key, base URL, and tenant_id
        - Conversation creation is called with empty user_id

    Expected:
        - ValueError should be raised with "user_id cannot be empty" message
        - API call should fail before making HTTP request
    """
    with pytest.raises(ValueError, match="user_id cannot be empty"):
        client.conversation.create(user_id="", chatbot_id="bot_789")


def test_create_conversation_missing_chatbot_id(client):
    """Test conversation creation with missing chatbot_id.

    Condition:
        - Client is initialized with valid API key, base URL, and tenant_id
        - Conversation creation is called with empty chatbot_id

    Expected:
        - ValueError should be raised with "chatbot_id cannot be empty" message
        - API call should fail before making HTTP request
    """
    with pytest.raises(ValueError, match="chatbot_id cannot be empty"):
        client.conversation.create(user_id="user_456", chatbot_id="")


def test_create_conversation_headers_included(client, mock_response):
    """Test that proper headers are included in the request.

    Condition:
        - Client is initialized with valid API key, base URL, and tenant_id
        - Mock response is configured with conversation data
        - Conversation creation is called to trigger HTTP request

    Expected:
        - Authorization header should be included with Bearer token
        - X-Tenant-ID header should be included with tenant_id value
        - Data should be sent as form data, not JSON
    """
    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = mock_response

        client.conversation.create(user_id="user_456", chatbot_id="bot_789")

        # Check that the post was called with proper headers
        call_args = mock_post.call_args
        headers = call_args[1]["headers"]

        assert headers["Authorization"] == "Bearer test_api_key"
        assert headers["X-Tenant-ID"] == "test_tenant"

        # Check that data is sent as form data, not JSON
        assert "data" in call_args[1]
        assert "json" not in call_args[1]


def test_create_conversation_without_tenant_id():
    """Test conversation creation without tenant_id.

    Condition:
        - Client is initialized without tenant_id parameter
        - Mock response is configured with conversation data
        - Conversation creation is called to trigger HTTP request

    Expected:
        - Conversation should be created successfully
        - X-Tenant-ID header should not be included in the request
        - Authorization header should still be included
    """
    client = GLChat(api_key="test_api_key", base_url="https://test-api.example.com")

    with patch("httpx.Client.post") as mock_post:
        mock_response = Mock()
        mock_response.json.return_value = {"conversation_id": "conv_123"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        response = client.conversation.create(user_id="user_456", chatbot_id="bot_789")

        assert response["conversation_id"] == "conv_123"

        # Check that X-Tenant-ID header is not included
        call_args = mock_post.call_args
        headers = call_args[1]["headers"]
        assert "X-Tenant-ID" not in headers

        # Check that data is sent as form data, not JSON
        assert "data" in call_args[1]
        assert "json" not in call_args[1]
