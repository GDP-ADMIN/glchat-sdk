"""Provides a base class for rate limiter service.

Authors:
    Kevin Susanto (kevin.susanto@gdplabs.id)

References:
    NONE
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseRateLimiterService(ABC):
    """A base class for tenant service."""

    @abstractmethod
    async def custom_identifier(self, **kwargs: Any) -> str:
        """Abstract method to get a custom identifier for rate limiting.

        Args:
            **kwargs (Any): Additional keyword arguments.

        Returns:
            str: A custom identifier for rate limiting.
        """
        raise NotImplementedError


    @abstractmethod
    async def setup_rate_limiter(self, **kwargs: Any) -> None:
        """Abstract method to set up the rate limiter.

        Args:
            **kwargs (Any): Additional keyword arguments.
        """
        raise NotImplementedError
