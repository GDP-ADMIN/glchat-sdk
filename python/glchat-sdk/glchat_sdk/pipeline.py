"""Pipeline handling for the GLChat Python client.

This module provides the PipelineAPI class for handling pipeline plugin operations
with the GLChat backend, including zip file uploads for plugin registration.

Authors:
    Hermes Vincentius Gani (hermes.v.gani@gdplabs.id)

References:
    None
"""

import logging
from pathlib import Path
from typing import Any, BinaryIO
from urllib.parse import urljoin

import httpx

from glchat_sdk.models import PipelineRequest

logger = logging.getLogger(__name__)

ZIP_FILE_TYPE = "application/zip"


class PipelineAPI:
    """Handles pipeline API operations for the GLChat API."""

    def __init__(self, client):
        self._client = client

    def _validate_zip_file(self, zip_file: str | Path | BinaryIO | bytes) -> None:
        """Validate zip file input.

        Args:
            zip_file (Union[str, Path, BinaryIO, bytes]): Zip file to validate

        Raises:
            ValueError: If zip_file is empty or invalid
            FileNotFoundError: If file path doesn't exist
        """
        if not zip_file:
            raise ValueError("zip_file cannot be empty")

        if isinstance(zip_file, str | Path):
            file_path = Path(zip_file)
            if not file_path.exists():
                raise FileNotFoundError(f"Zip file not found: {file_path}")
            if not file_path.suffix.lower() == ".zip":
                raise ValueError(f"File must be a zip file: {file_path}")

    def _prepare_request_data(self) -> dict[str, Any]:
        """Prepare request data for the API call.

        Returns:
            dict containing the prepared request data
        """
        request = PipelineRequest()
        return request.model_dump(exclude_none=True)

    def _prepare_headers(self) -> dict[str, str]:
        """Prepare headers for the API request.

        Returns:
            dict containing the request headers
        """
        headers = {}
        if self._client.api_key:
            headers["Authorization"] = f"Bearer {self._client.api_key}"
        return headers

    def _process_zip_file(
        self, zip_file: str | Path | BinaryIO | bytes
    ) -> tuple[str, str | BinaryIO | bytes, str]:
        """Process the zip file and return the file tuple for httpx.

        Args:
            zip_file (Union[str, Path, BinaryIO, bytes]): Zip file to process

        Returns:
            tuple of (field_name, (filename, file_content, content_type))

        Raises:
            ValueError: If file type is not supported
            FileNotFoundError: If file path doesn't exist
        """
        if isinstance(zip_file, str | Path):
            # File path
            file_path = Path(zip_file)
            if not file_path.exists():
                raise FileNotFoundError(f"Zip file not found: {file_path}")
            with open(file_path, "rb") as f:
                return ("file", (file_path.name, f.read(), ZIP_FILE_TYPE))
        elif isinstance(zip_file, bytes):
            # Raw bytes
            return ("file", ("plugin.zip", zip_file, ZIP_FILE_TYPE))
        elif hasattr(zip_file, "read"):
            # File-like object - pass directly to avoid memory issues
            filename = getattr(zip_file, "name", "plugin.zip")
            return ("file", (filename, zip_file, ZIP_FILE_TYPE))
        else:
            raise ValueError(f"Unsupported file type: {type(zip_file)}")

    def _make_request(
        self,
        url: str,
        data: dict[str, Any],
        zip_file_tuple: tuple[str, tuple[str, str | BinaryIO | bytes, str]],
        headers: dict[str, str],
    ) -> httpx.Response:
        """Make the HTTP request for pipeline plugin registration.

        Args:
            url (str): API endpoint URL
            data (dict[str, Any]): Request data
            zip_file_tuple (tuple[str, tuple[str, str | BinaryIO | bytes, str]]): Prepared zip data
            headers (dict[str, str]): Request headers

        Returns:
            httpx.Response: The HTTP response

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        timeout = httpx.Timeout(self._client.timeout, read=self._client.timeout)

        with httpx.Client(timeout=timeout) as client:
            response = client.post(
                url,
                data=data,
                files=[zip_file_tuple],
                headers=headers,
            )
            response.raise_for_status()
            return response

    def register(
        self,
        zip_file: str | Path | BinaryIO | bytes,
    ) -> dict[str, Any]:
        """
        Register a pipeline plugin by uploading a zip file to the GLChat API.

        Args:
            zip_file (Union[str, Path, BinaryIO, bytes]): Zip file containing the plugin
                (filepath, binary, file object, or bytes)

        Returns:
            dict[str, Any]: Response from the API containing registration details

        Raises:
            ValueError: If input validation fails
            FileNotFoundError: If zip file path doesn't exist
            httpx.HTTPStatusError: If the API request fails
        """
        self._validate_zip_file(zip_file)

        logger.debug("Registering pipeline plugin with zip file")

        url = urljoin(self._client.base_url, "register-pipeline-plugin")
        data = self._prepare_request_data()
        headers = self._prepare_headers()
        zip_file_tuple = self._process_zip_file(zip_file)

        response = self._make_request(url, data, zip_file_tuple, headers)

        return response.json()

    def unregister(
        self,
        plugin_ids: list[str],
    ) -> dict[str, Any]:
        """
        Unregister pipeline plugins by sending their IDs to the GLChat API.

        Args:
            plugin_ids (list[str]): List of plugin IDs to unregister

        Returns:
            dict[str, Any]: Response from the API containing unregistration details

        Raises:
            ValueError: If input validation fails
            httpx.HTTPStatusError: If the API request fails
        """
        if not plugin_ids:
            raise ValueError("plugin_ids cannot be empty")

        logger.debug("Unregistering pipeline plugins: %s", plugin_ids)

        url = urljoin(self._client.base_url, "unregister-pipeline-plugin")
        headers = self._prepare_headers()

        timeout = httpx.Timeout(self._client.timeout, read=self._client.timeout)

        with httpx.Client(timeout=timeout) as client:
            response = client.post(
                url,
                json=plugin_ids,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
