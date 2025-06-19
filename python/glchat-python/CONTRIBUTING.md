# Contributing

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
- API key authentication

Each test is documented with clear descriptions of what is being tested and why.
