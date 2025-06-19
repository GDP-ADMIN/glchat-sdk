<p align="center">
  <a href="https://docs.glair.ai" target="_blank">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://glair-chart.s3.ap-southeast-1.amazonaws.com/images/glair-horizontal-logo-blue.png">
      <source media="(prefers-color-scheme: light)" srcset="https://glair-chart.s3.ap-southeast-1.amazonaws.com/images/glair-horizontal-logo-color.png">
      <img alt="GLAIR" src="https://glair-chart.s3.ap-southeast-1.amazonaws.com/images/glair-horizontal-logo-color.png" width="180" height="60" style="max-width: 100%;">
    </picture>
  </a>
</p>

<p align="center">
  GLChat Python SDK
<p>

<p align="center">
    <a href="https://github.com/glair-ai/glchat-sdk/releases"><img src="https://img.shields.io/npm/v/@gdplabs/glchat-sdk" alt="Latest Release"></a>
    <a href="https://github.com/glair-ai/glchat-sdk/blob/main/LICENSE"><img src="https://img.shields.io/npm/l/@gdplabs/glchat-sdk" alt="License"></a>
</p>

A lightweight, flexible Python client for interacting with the GLChat Backend API, providing a simple interface to send messages and receive streaming responses. Built with an OpenAI-like API design for familiarity and ease of use.

## Overview

GLChat Python Client is a Python library that simplifies interaction with the GLChat service. It provides a clean, intuitive API for sending messages, handling file attachments, and processing streaming responses, enabling rapid development of chat applications.

## Features

- **OpenAI-like API**: Familiar interface following the OpenAI SDK pattern
- **Authentication Support**: Built-in API key authentication
- **Simple API**: Send messages and receive responses with minimal code
- **Streaming Support**: Process responses in real-time as they arrive
- **File Integration**: Easily attach and send files with your messages
- **Type Safety**: Comprehensive type hints for better development experience
- **Flexible Response Handling**: Choose between streaming or complete text responses
- **Memory Efficient**: Optimized file handling for large files

## Installation

This project uses [uv](https://docs.astral.sh/uv/getting-started/) for dependency management. To install the package:

```bash
# Change to the glchat-python directory
cd python/glchat-python

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

# Initialize the GLChat client with your API key
client = GLChatClient(api_key="your-api-key")

# Send a message to the chatbot and receive a streaming response
for chunk in client.message.create(
    chatbot_id="your-chatbot-id",
    message="Hello!"
):
    print(chunk.decode("utf-8"), end="")
```

Note: Make sure you have the correct chatbot ID and API key before running example.

## Advanced Usage

### Sending Messages with Files

```python
from pathlib import Path
from glchat_python import GLChatClient

client = GLChatClient(api_key="your-api-key")

# Send message with file attachment
for chunk in client.message.create(
    chatbot_id="your-chatbot-id",
    message="What's in this file?",
    files=[Path("/path/to/your/file.txt")],
    user_id="user@example.com",
    conversation_id="your-conversation-id",
    model_name="openai/gpt-4o-mini"
):
    print(chunk.decode("utf-8"), end="")
```

### Using Different File Types

```python
from glchat_python import GLChatClient
import io

client = GLChatClient(api_key="your-api-key")

# File path
file_path = "/path/to/file.txt"

# File-like object
file_obj = io.BytesIO(b"file content")

# Raw bytes
file_bytes = b"file content"

# Send with different file types
for chunk in client.message.create(
    chatbot_id="your-chatbot-id",
    message="Process these files",
    files=[file_path, file_obj, file_bytes]
):
    print(chunk.decode("utf-8"), end="")
```

## API Reference

### GLChatClient

The main client class for interacting with the GLChat API.

#### Initialization

```python
client = GLChatClient(
    api_key: str | None = None,
    base_url: str | None = None,
    timeout: float = 60.0
)
```

**Parameters:**

- `api_key`: Your GLChat API key for authentication
- `base_url`: Custom base URL for the GLChat API (optional)
- `timeout`: Request timeout in seconds (default: 60.0)

#### Methods

##### message.create

Creates a streaming response from the GLChat API.

```python
response_stream = client.message.create(
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
    files: List[Union[str, Path, BinaryIO, bytes]] | None = None,
    stream_id: str | None = None,
    metadata: str | None = None,
    model_name: str | None = None,
    anonymize_em: bool | None = None,
    anonymize_lm: bool | None = None,
    use_cache: bool | None = None,
    search_type: str | None = None
) -> Iterator[bytes]
```

**Parameters:**

- `chatbot_id`: Required chatbot identifier
- `message`: Required user message
- `files`: List of files (filepath, binary, file object, or bytes)
- `**kwargs`: Additional message parameters (see MessageRequest model)

**Returns:**

- `Iterator[bytes]`: Streaming response chunks

## File Support

The client supports various file input types with optimized memory handling:

- **File paths** (string or Path object)
- **Binary data** (bytes)
- **File-like objects** (with read() method) - passed directly to avoid memory issues

## Authentication

The client supports API key authentication. When an API key is provided, it's automatically included in the Authorization header for all requests:

```python
client = GLChatClient(api_key="your-api-key")
# API key is automatically used in requests
```

## Error Handling

The client uses `httpx` for HTTP requests and will raise appropriate exceptions for HTTP errors. Make sure to handle these exceptions in your code.
