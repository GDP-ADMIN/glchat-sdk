"""Provides a base class for tenant service.

Authors:
    Ryan Ignatius Hadiwijaya (ryan.i.hadiwijaya@gdplabs.id)

References:
    NONE
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseTenantService(ABC):
    """A base class for tenant service."""

    @abstractmethod
    async def set_tenant_context(self, **kwargs: Any):
        """Abstract method to set the tenant context.

        Args:
            **kwargs: Additional keyword arguments for tenant context setting.
                The parameters are Fast API from Request object.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError

    @abstractmethod
    def get_current_tenant(self) -> str:
        """Abstract method to get the tenant id.

        Returns:
            str: tenant id.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError
