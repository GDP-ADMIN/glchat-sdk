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
from typing import Any
from urllib.parse import urljoin

import httpx

from glchat_sdk.models import PipelineRequest

logger = logging.getLogger(__name__)

ZIP_FILE_TYPE = "application/zip"


class PipelineAPI:
    """Handles pipeline API operations for the GLChat API."""

    def __init__(self, client):
        self._client = client

    def _validate_zip_file(self, zip_path_file: str) -> None:
        """Validate zip file input.

        Args:
            zip_path_file (str): Zip file path to validate

        Raises:
            ValueError: If zip_path_file is empty or invalid
            FileNotFoundError: If file path doesn't exist
        """
        if not zip_path_file:
            raise ValueError("zip_path_file cannot be empty")

        file_path = Path(zip_path_file)
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

    def _process_zip_file(self, zip_path_file: str) -> tuple[str, bytes, str]:
        """Process the zip file and return the file tuple for httpx.

        Args:
            zip_path_file (str): Zip file path to process

        Returns:
            tuple of (field_name, (filename, file_content, content_type))

        Raises:
            FileNotFoundError: If file path doesn't exist
        """
        file_path = Path(zip_path_file)
        if not file_path.exists():
            raise FileNotFoundError(f"Zip file not found: {file_path}")
        with open(file_path, "rb") as f:
            return ("zip_file", (file_path.name, f.read(), ZIP_FILE_TYPE))

    def _make_request(
        self,
        url: str,
        data: dict[str, Any],
        zip_file_tuple: tuple[str, tuple[str, bytes, str]],
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
        zip_path_file: str,
    ) -> dict[str, Any]:
        """
        Register a pipeline plugin by uploading a zip file to the GLChat API.

        Args:
            zip_path_file (str): Path to the zip file containing the plugin

        Returns:
            dict[str, Any]: Response from the API containing registration details

        Raises:
            TypeError: If zip_path_file is not a string
            ValueError: If input validation fails
            FileNotFoundError: If zip file path doesn't exist
            httpx.HTTPStatusError: If the API request fails
        """
        if not isinstance(zip_path_file, str):
            raise TypeError(f"zip_path_file must be a string, got {type(zip_path_file).__name__}")

        self._validate_zip_file(zip_path_file)

        logger.debug("Registering pipeline plugin with zip file")

        url = urljoin(self._client.base_url, "register-pipeline-plugin")
        data = self._prepare_request_data()
        headers = self._prepare_headers()
        zip_file_tuple = self._process_zip_file(zip_path_file)

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
