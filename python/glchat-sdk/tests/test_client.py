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
    return GLChat(api_key="test_api_key", base_url="https://test-api.example.com")


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

        response = client.message.create(chatbot_id="test-bot", message="Hello", files=[test_bytes])

        chunks = list(response)
        assert chunks == [b"Hello", b" ", b"World"]
        mock_stream.assert_called_once()


def test_send_message_with_file_object(client, mock_response):
    """Test sending message with a file-like object."""
    file_obj = io.BytesIO(b"test content")
    file_obj.name = "test.txt"

    with patch("httpx.Client.stream") as mock_stream:
        mock_stream.return_value.__enter__.return_value = mock_response

        response = client.message.create(chatbot_id="test-bot", message="Hello", files=[file_obj])

        chunks = list(response)
        assert chunks == [b"Hello", b" ", b"World"]
        mock_stream.assert_called_once()


def test_send_message_with_invalid_file_type(client):
    """Test sending message with invalid file type."""
    with pytest.raises(ValueError, match="Unsupported file type"):
        list(
            client.message.create(
                chatbot_id="test-bot",
                message="Hello",
                files=[123],  # Invalid file type
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
        client = GLChat(api_key="test_api_key")
        assert client.base_url == "https://chat.gdplabs.id/api/proxy/"


@pytest.fixture
def mock_pipeline_response():
    """Create a mock pipeline response."""
    mock = Mock()
    mock.json.return_value = {"status": "success", "plugin_id": "test-plugin-123"}
    mock.raise_for_status = Mock()
    return mock


def test_pipeline_register_with_file_path(client, mock_pipeline_response, tmp_path):
    """Test pipeline plugin registration with file path."""
    # Create a temporary zip file
    test_zip = tmp_path / "test_plugin.zip"
    test_zip.write_bytes(b"fake zip content")

    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = mock_pipeline_response

        response = client.pipeline.register(str(test_zip))

        assert response == {"status": "success", "plugin_id": "test-plugin-123"}
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "register-pipeline-plugin" in call_args[0][0]
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_api_key"


def test_pipeline_register_with_bytes(client, mock_pipeline_response):
    """Test pipeline plugin registration with bytes data."""
    test_bytes = b"fake zip content"

    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = mock_pipeline_response

        response = client.pipeline.register(test_bytes)

        assert response == {"status": "success", "plugin_id": "test-plugin-123"}
        mock_post.assert_called_once()


def test_pipeline_register_with_file_object(client, mock_pipeline_response):
    """Test pipeline plugin registration with file-like object."""
    file_obj = io.BytesIO(b"fake zip content")
    file_obj.name = "test_plugin.zip"

    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = mock_pipeline_response

        response = client.pipeline.register(file_obj)

        assert response == {"status": "success", "plugin_id": "test-plugin-123"}
        mock_post.assert_called_once()


def test_pipeline_register_with_empty_input(client):
    """Test pipeline plugin registration with empty input."""
    with pytest.raises(ValueError, match="zip_file cannot be empty"):
        client.pipeline.register("")


def test_pipeline_register_with_nonexistent_file(client):
    """Test pipeline plugin registration with nonexistent file."""
    with pytest.raises(FileNotFoundError, match="Zip file not found"):
        client.pipeline.register("nonexistent.zip")


def test_pipeline_register_with_non_zip_file(client, tmp_path):
    """Test pipeline plugin registration with non-zip file."""
    # Create a temporary non-zip file
    test_file = tmp_path / "test.txt"
    test_file.write_text("not a zip file")

    with pytest.raises(ValueError, match="File must be a zip file"):
        client.pipeline.register(str(test_file))


def test_pipeline_register_with_invalid_file_type(client):
    """Test pipeline plugin registration with invalid file type."""
    with pytest.raises(ValueError, match="Unsupported file type"):
        client.pipeline.register(123)  # Invalid file type


def test_pipeline_unregister_success(client, mock_pipeline_response):
    """Test successful pipeline plugin unregistration."""
    plugin_ids = ["plugin-1", "plugin-2", "plugin-3"]

    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = mock_pipeline_response

        response = client.pipeline.unregister(plugin_ids)

        assert response == {"status": "success", "plugin_id": "test-plugin-123"}
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "unregister-pipeline-plugin" in call_args[0][0]
        assert call_args[1]["json"] == plugin_ids
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_api_key"


def test_pipeline_unregister_with_empty_list(client):
    """Test pipeline plugin unregistration with empty list."""
    with pytest.raises(ValueError, match="plugin_ids cannot be empty"):
        client.pipeline.unregister([])


def test_pipeline_unregister_with_none_input(client):
    """Test pipeline plugin unregistration with None input."""
    with pytest.raises(ValueError, match="plugin_ids cannot be empty"):
        client.pipeline.unregister(None)


def test_pipeline_register_http_error(client, tmp_path):
    """Test pipeline plugin registration with HTTP error."""
    test_zip = tmp_path / "test_plugin.zip"
    test_zip.write_bytes(b"fake zip content")

    with patch("httpx.Client.post") as mock_post:
        mock_post.side_effect = Exception("HTTP Error")

        with pytest.raises(Exception, match="HTTP Error"):
            client.pipeline.register(str(test_zip))


def test_pipeline_unregister_http_error(client):
    """Test pipeline plugin unregistration with HTTP error."""
    plugin_ids = ["plugin-1"]

    with patch("httpx.Client.post") as mock_post:
        mock_post.side_effect = Exception("HTTP Error")

        with pytest.raises(Exception, match="HTTP Error"):
            client.pipeline.unregister(plugin_ids)


def test_pipeline_register_with_path_object(client, mock_pipeline_response, tmp_path):
    """Test pipeline plugin registration with Path object."""
    from pathlib import Path

    test_zip = tmp_path / "test_plugin.zip"
    test_zip.write_bytes(b"fake zip content")

    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = mock_pipeline_response

        response = client.pipeline.register(Path(test_zip))

        assert response == {"status": "success", "plugin_id": "test-plugin-123"}
        mock_post.assert_called_once()


def test_pipeline_register_with_file_object_no_name(client, mock_pipeline_response):
    """Test pipeline plugin registration with file object without name attribute."""
    file_obj = io.BytesIO(b"fake zip content")
    # No name attribute set

    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = mock_pipeline_response

        response = client.pipeline.register(file_obj)

        assert response == {"status": "success", "plugin_id": "test-plugin-123"}
        mock_post.assert_called_once()


def test_client_pipeline_attribute_exists(client):
    """Test that the pipeline attribute exists on the client."""
    assert hasattr(client, "pipeline")
    assert client.pipeline is not None


def test_pipeline_api_has_required_methods(client):
    """Test that the pipeline API has the required methods."""
    assert hasattr(client.pipeline, "register")
    assert hasattr(client.pipeline, "unregister")
    assert callable(client.pipeline.register)
    assert callable(client.pipeline.unregister)
