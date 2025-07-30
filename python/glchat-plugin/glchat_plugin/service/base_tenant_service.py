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
    async def get_tenant_id(self, **kwargs: Any) -> str | None:
        """Abstract method to get the tenant id.

        Args:
            **kwargs (Any): Additional keyword arguments for tenant identification.
                The kwargs are Fast API Request object.

        Returns:
            str | None: tenant id, None if not found.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
        raise NotImplementedError
