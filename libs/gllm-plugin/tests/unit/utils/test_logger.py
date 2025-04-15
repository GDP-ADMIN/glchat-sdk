"""Tests for the logger utility.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import logging
from io import StringIO
from unittest.mock import patch

import pytest
from colorama import Fore, Style

from gllm_plugin.utils.logger import (
    LOGGER_NAME,
    ColoredFormatter,
    logger,
    stream_handler,
)


def test_logger_basic_setup():
    """Test the basic setup of the logger instance."""
    assert logger.name == LOGGER_NAME
    assert logger.level == logging.INFO
    assert not logger.propagate
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)


def test_colored_formatter_format():
    """Test the ColoredFormatter adds correct color codes."""
    formatter = ColoredFormatter()
    log_record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test_path",
        lineno=10,
        msg="Test info message",
        args=(),
        exc_info=None,
        func="test_func",
    )
    formatted_message = formatter.format(log_record)
    expected_message = f"{Fore.GREEN}Test info message{Style.RESET_ALL}"
    assert expected_message in formatted_message

    log_record.levelno = logging.WARNING
    log_record.msg = "Test warning message"
    formatted_message = formatter.format(log_record)
    expected_message = f"{Fore.YELLOW}Test warning message{Style.RESET_ALL}"
    assert expected_message in formatted_message

    log_record.levelno = logging.ERROR
    log_record.msg = "Test error message"
    formatted_message = formatter.format(log_record)
    expected_message = f"{Fore.RED}Test error message{Style.RESET_ALL}"
    assert expected_message in formatted_message

    log_record.levelno = logging.DEBUG  # Default color
    log_record.msg = "Test debug message"
    formatted_message = formatter.format(log_record)
    expected_message = f"{Style.RESET_ALL}Test debug message{Style.RESET_ALL}"
    assert expected_message in formatted_message

    log_record.levelno = logging.CRITICAL
    log_record.msg = "Test critical message"
    formatted_message = formatter.format(log_record)
    expected_message = f"{Fore.MAGENTA}Test critical message{Style.RESET_ALL}"
    assert expected_message in formatted_message

    # Test unknown level (should default to WHITE)
    log_record.levelno = 99  # Unknown level
    log_record.msg = "Test unknown level message"
    formatted_message = formatter.format(log_record)
    expected_message = f"{Fore.WHITE}Test unknown level message{Style.RESET_ALL}"
    assert expected_message in formatted_message


def test_logger_output():
    """Test that the logger outputs messages correctly with the formatter."""
    # Capture logs
    log_stream = StringIO()
    # Replace existing stream handler with one that writes to StringIO
    temp_handler = logging.StreamHandler(log_stream)
    temp_handler.setFormatter(stream_handler.formatter)  # Use the same formatter

    # Temporarily replace the handler
    original_handlers = logger.handlers[:]
    logger.handlers = [temp_handler]

    try:
        test_message = "This is an info test log"
        logger.info(test_message)
        log_stream.seek(0)
        output = log_stream.read()

        # Check for color codes and message content
        assert Fore.GREEN in output
        assert Style.RESET_ALL in output
        assert test_message in output
        assert f" {logging.getLevelName(logging.INFO)[0]}]" in output  # Check level initial

    finally:
        # Restore original handlers
        logger.handlers = original_handlers
