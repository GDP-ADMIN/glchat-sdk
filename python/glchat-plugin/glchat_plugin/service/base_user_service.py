"""Provides a base class for user service.

Authors:
    Immanuel Rhesa (immanuel.rhesa@gdplabs.id)
    Hermes Vincentius Gani (hermes.v.gani@gdplabs.id)

References:
    NONE
"""

from abc import ABC, abstractmethod


class BaseUserService(ABC):
    """A base class for user service."""

    @abstractmethod
    async def get_user_id(self, **kwargs) -> str:
        """Abstract method to get the user id.

        Args:
            **kwargs: Additional keyword arguments for user identification.

        Returns:
            str: user id.
        """

    @abstractmethod
    async def register(self, **kwargs):
        """Abstract method to register a new user.

        Args:
            **kwargs: Additional keyword arguments for user registration.
        """

    @abstractmethod
    async def login(self, **kwargs):
        """Abstract method to authenticate and login a user.

        Args:
            **kwargs: Additional keyword arguments for user login.
        """

    @abstractmethod
    async def get_applications(self, **kwargs):
        """Abstract method to get user applications.

        Args:
            **kwargs: Additional keyword arguments for retrieving applications.
        """

    @abstractmethod
    async def set_user_applications(self, **kwargs):
        """Abstract method to set user applications.

        Args:
            **kwargs: Additional keyword arguments for setting user applications.
        """
