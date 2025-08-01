<p align="center">
  <a href="https://docs.glair.ai" target="_blank">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://assets.analytics.glair.ai/generative/img/glchat-beta-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://assets.analytics.glair.ai/generative/img/glchat-beta-light.svg">
      <img alt="GLAIR" src="https://assets.analytics.glair.ai/generative/img/glchat-beta-light.svg" width="180" height="60" style="max-width: 100%;">
    </picture>
  </a>
</p>

<p align="center">
  🤖 GLChat Python SDK 🐍
<p>

<p align="center">
    <a href="https://pypi.org/project/glchat-sdk/"><img src="https://img.shields.io/pypi/v/glchat-sdk" alt="PyPI Latest Release"></a>
    <a href="https://github.com/GDP-ADMIN/glchat-sdk/blob/main/python/glchat-sdk/LICENSE"><img src="https://img.shields.io/pypi/l/glchat-sdk" alt="License"></a>
</p>

A lightweight, flexible Python client for interacting with the GLChat Backend API, providing a simple interface to send messages and receive streaming responses. Built with an OpenAI-like API design for familiarity and ease of use.

## 📋 Overview

GLChat Python Client is a Python library that simplifies interaction with the GLChat service. It provides a clean, intuitive API for sending messages, handling file attachments, and processing streaming responses, enabling rapid development of chat applications.

## 📋 Requirements

**Python 3.11.x** or higher is required.

## ✨ Features

- **🔌 OpenAI-like API**: Familiar interface following the OpenAI SDK pattern
- **🔐 Authentication Support**: Built-in API key authentication
- **🚀 Simple API**: Send messages and receive responses with minimal code
- **⚡ Streaming Support**: Process responses in real-time as they arrive
- **📎 File Integration**: Easily attach and send files with your messages
- **🎯 Type Safety**: Comprehensive type hints for better development experience
- **🔄 Flexible Response Handling**: Choose between streaming or complete text responses
- **💾 Memory Efficient**: Optimized file handling for large files

## 📦 Installation

To install the package:

```bash
pip install glchat-sdk
```

After installation, you can verify it works by trying to import it from any directory:

```python
from glchat_sdk import GLChat
```

## 🚀 Quick Start

Creating a chat client with GLChat is incredibly simple:

```python
from glchat_sdk import GLChat

# Initialize the GLChat client with your API key
client = GLChat(api_key="your-api-key")

# Send a message to the chatbot and receive a streaming response
for chunk in client.message.create(
    chatbot_id="your-chatbot-id",
    message="Hello!"
):
    print(chunk.decode("utf-8"), end="")
```

Note: Make sure you have the correct chatbot ID and API key before running example.

### 🔐 Environment Variables

GLChat uses `os.getenv()` to read environment variables. **You are responsible for loading environment variables** in your application before initializing the GLChat client. You can use libraries like `python-dotenv`, `python-decouple`, or set them directly in your shell.

**Available environment variables:**

- `GLCHAT_API_KEY`: Your GLChat API key for authentication
- `GLCHAT_BASE_URL`: Custom base URL for the GLChat API (optional)

**Example using python-dotenv:**

First, install python-dotenv:

```bash
pip install python-dotenv
```

Create a `.env` file:

```bash
GLCHAT_API_KEY=your-api-key
GLCHAT_BASE_URL=https://your-custom-endpoint.com/api/
```

Load environment variables in your code:

```python
from dotenv import load_dotenv
from glchat_sdk import GLChat

# Load environment variables from .env file
load_dotenv()

# Will automatically use environment variables
client = GLChat()
```

**Example using shell export:**

```bash
export GLCHAT_API_KEY="your-api-key"
export GLCHAT_BASE_URL="https://your-custom-endpoint.com/api/"
```

Then initialize the client without parameters:

```python
from glchat_sdk import GLChat

# Will automatically use environment variables
client = GLChat()
```

## 🔧 Advanced Usage

### 📤 Sending Messages with Files

```python
from pathlib import Path
from glchat_sdk import GLChat

client = GLChat(api_key="your-api-key")

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

### 📁 Using Different File Types

```python
from glchat_sdk import GLChat
import io

client = GLChat(api_key="your-api-key")

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

## 📚 API Reference

### GLChat

The main client class for interacting with the GLChat API.

#### 🔧 Initialization

```python
client = GLChat(
    api_key: str | None = None,
    base_url: str | None = None,
    timeout: float = 60.0
)
```

**Parameters:**

- `api_key`: Your GLChat API key for authentication 🔑 (or set GLCHAT_API_KEY env var)
- `base_url`: Custom base URL for the GLChat API (optional, or set GLCHAT_BASE_URL env var) 🌐
- `timeout`: Request timeout in seconds (default: 60.0) ⏱️

#### Methods

##### 💬 message.create

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

- `chatbot_id`: Required chatbot identifier 🤖
- `message`: Required user message 💬
- `parent_id`: Parent message ID for threading (optional) 🧵
- `source`: Source identifier for the message (optional) 📍
- `quote`: Quoted message content (optional) 💭
- `user_id`: User identifier (optional) 👤
- `conversation_id`: Conversation identifier (optional) 💬
- `user_message_id`: User message identifier (optional) 🆔
- `assistant_message_id`: Assistant message identifier (optional) 🤖
- `chat_history`: Chat history context (optional) 📚
- `files`: List of files (filepath, binary, file object, or bytes) (optional) 📎
- `stream_id`: Stream identifier (optional) 🌊
- `metadata`: Additional metadata (optional) 📋
- `model_name`: Model name to use for generation (optional) 🧠
- `anonymize_em`: Whether to anonymize embeddings (optional) 🕵️
- `anonymize_lm`: Whether to anonymize language model (optional) 🕵️
- `use_cache`: Whether to use cached responses (optional) 💾
- `search_type`: Type of search to perform (optional) 🔍

**Returns:**

- `Iterator[bytes]`: Streaming response chunks 📡

## 📁 File Support

The client supports various file input types with optimized memory handling:

- **📂 File paths** (string or Path object)
- **💾 Binary data** (bytes)
- **📄 File-like objects** (with read() method) - passed directly to avoid memory issues

## 🔐 Authentication

The client supports API key authentication with flexible configuration options. The API key can be provided either as a parameter during initialization or through environment variables.

### 🔑 API Key Configuration

**Option 1: Direct Parameter**

```python
client = GLChat(api_key="your-api-key")
```

**Option 2: Environment Variable**

```bash
export GLCHAT_API_KEY="your-api-key"
```

```python
client = GLChat()  # Automatically uses GLCHAT_API_KEY environment variable
```

**Option 3: Priority System**

```python
# Parameter takes priority over environment variable
client = GLChat(api_key="explicit-api-key")  # Uses explicit key even if env var is set
```

### 🔒 Authentication Headers

When an API key is provided (via parameter or environment variable), it's automatically included in the Authorization header for all requests:

```python
# API key is automatically used in requests 🔑
client = GLChat(api_key="your-api-key")
for chunk in client.message.create(chatbot_id="your-chatbot-id", message="Hello!"):
    print(chunk.decode("utf-8"), end="")
```

### ⚠️ Required Configuration

**API key is required** - you must provide it either:

- As the `api_key` parameter when initializing the client, OR
- Set the `GLCHAT_API_KEY` environment variable

If neither is provided, the client will raise a `ValueError`:

```python
client = GLChat()  # Raises ValueError if GLCHAT_API_KEY is not set
```

## ⚠️ Error Handling

The client uses `httpx` for HTTP requests and will raise appropriate exceptions for HTTP errors. Make sure to handle these exceptions in your code.
