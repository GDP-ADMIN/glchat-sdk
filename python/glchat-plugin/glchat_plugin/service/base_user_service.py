"""Provides a base class for user service.

Authors:
    Immanuel Rhesa (immanuel.rhesa@gdplabs.id)
"""

from abc import ABC, abstractmethod

from fastapi import Request


class BaseUserService(ABC):
    """A base class for user service."""

    @abstractmethod
    async def get_user_id(self, request: Request) -> str:
        """Abstract method to get the user id.

        Returns:
            str: user id.
        """
