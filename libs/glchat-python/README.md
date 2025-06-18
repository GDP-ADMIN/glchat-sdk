# GLChat Python Client

A lightweight, flexible Python client for interacting with the GLChat Backend API, providing a simple interface to send messages and receive streaming responses.

## Overview

GLChat Python Client is a Python library that simplifies interaction with the GLChat service. It provides a clean, intuitive API for sending messages, handling file attachments, and processing streaming responses, enabling rapid development of chat applications.

## Features

- **Simple API**: Send messages and receive responses with minimal code
- **Streaming Support**: Process responses in real-time as they arrive
- **File Integration**: Easily attach and send files with your messages
- **Type Safety**: Comprehensive type hints for better development experience
- **Flexible Response Handling**: Choose between streaming or complete text responses

## Installation

This project uses `uv` for dependency management. To install the package:

```bash
# Change to the glchat-python directory
cd libs/glchat-python

# Install dependencies using uv
uv pip install -e .
```

The `-e` flag installs the package in "editable" mode, which means:

- The package is installed in your Python environment
- You can import and use it from any directory
- Changes to the source code will be reflected immediately without needing to reinstall
- The package is linked to your development directory, making it easier to develop and test

After installation, you can verify it works by trying to import it from any directory:

```python
from glchat_python import GLChatClient
```

## Quick Start

Creating a chat client with GLChat is incredibly simple:

```python
from glchat_python import GLChatClient

# Initialize the client
client = GLChatClient()

# Send a message and get streaming response
response_stream = client.send_message(
    chatbot_id="your-chatbot-id",
    message="Hello!"
)

# Process streaming response
for chunk in response_stream:
    print(chunk.decode("utf-8"), end="")
```

You can also run this as a one-liner using `uv run python -c "..."` if you prefer.

Note: Make sure you have the correct chatbot ID and any required environment variables set before running these examples.

## Advanced Usage

### Sending Messages with Files

```python
from pathlib import Path
from glchat_python import GLChatClient

client = GLChatClient()

# Send message with file attachment
response_stream = client.send_message(
    chatbot_id="your-chatbot-id",
    message="What's in this file?",
    files=[Path("/path/to/your/file.txt")],
    user_id="user@example.com",
    conversation_id="your-conversation-id",
    model_name="openai/gpt-4o-mini"
)

# Process streaming response
for chunk in response_stream:
    print(chunk.decode("utf-8"), end="")
```

## API Reference

### GLChatClient

The main client class for interacting with the GLChat API.

#### Initialization

```python
client = GLChatClient(base_url="https://your-api-url")
```

#### Methods

##### send_message

Sends a message and returns a streaming response.

```python
response_stream = client.send_message(
    chatbot_id: str,
    message: str,
    parent_id: Optional[str] = None,
    source: Optional[str] = None,
    quote: Optional[str] = None,
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    user_message_id: Optional[str] = None,
    assistant_message_id: Optional[str] = None,
    chat_history: Optional[str] = None,
    files: Optional[List[Union[str, Path, BinaryIO, bytes]]] = None,
    stream_id: Optional[str] = None,
    metadata: Optional[str] = None,
    model_name: Optional[str] = None,
    anonymize_em: Optional[bool] = None,
    anonymize_lm: Optional[bool] = None,
    use_cache: Optional[bool] = None,
    search_type: Optional[str] = None
) -> Iterator[bytes]
```

## File Support

The client supports various file input types:

- File paths (string or Path object)
- Binary data (bytes)
- File-like objects (with read() method)

## Error Handling

The client uses `httpx` for HTTP requests and will raise appropriate exceptions for HTTP errors. Make sure to handle these exceptions in your code.

## Contributing

Please refer to this [Python Style Guide](https://docs.google.com/document/d/1uRggCrHnVfDPBnG641FyQBwUwLoFw0kTzNqRm92vUwM/edit?usp=sharing)
to get information about code style, documentation standard, and SCA that you need to use when contributing to this project

## Testing

The project uses pytest for testing. The test suite includes comprehensive tests for all major functionality of the GLChatClient.

### Development Setup

1. Install dependencies using uv:

```bash
# Install main dependencies
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```

### Running Tests

You can run tests using either uv or pytest directly:

```bash
# Using uv
uv run pytest

# Using uv with specific options
uv run pytest -v  # verbose output
uv run pytest -s  # show print statements
uv run pytest tests/test_client.py  # run specific test file
uv run pytest tests/test_client.py::test_send_message_basic  # run specific test

# Using pytest directly (if installed)
pytest
pytest -v
pytest -s
pytest tests/test_client.py
pytest tests/test_client.py::test_send_message_basic
```

### Test Coverage

The project uses pytest-cov for test coverage reporting. Coverage reports show which parts of the code are tested and which are not.

```bash
# Run tests with coverage report
uv run pytest --cov

# Generate HTML coverage report
uv run pytest --cov --cov-report=html

# Generate XML coverage report (useful for CI)
uv run pytest --cov --cov-report=xml
```

The coverage configuration is set up in `pyproject.toml` to:

- Track coverage for the `glchat_python` package
- Exclude test files and `__init__.py` files
- Show missing lines in the terminal report

The test suite includes tests for:

- Basic message sending
- File handling (file paths, bytes, file objects)
- Error cases
- Additional parameters
- Streaming response handling

Each test is documented with clear descriptions of what is being tested and why.
