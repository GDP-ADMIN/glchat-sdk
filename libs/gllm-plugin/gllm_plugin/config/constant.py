"""Constants for the API.

Authors:
    Ryan Ignatius Hadiwijaya (ryan.i.hadiwijaya@gdplabs.id)

References:
    None
"""

from enum import StrEnum

import elastic_transport
import requests
import urllib3


class SearchType(StrEnum):
    """The type of search to perform.

    Values:
        NORMAL: Get answer from chatbot knowledge.
        SMART: Get more relevant information from your stored documents and knowledge base.
            Knowledge Search is an AI with specialized knowledge. No agents are available in this mode.
        WEB: Get more relevant information from the web.
            Web Search uses real-time data. Agent selection isn't available in this mode.
    """

    NORMAL = "normal"
    SMART = "smart"
    WEB = "web"


DEFAULT_RETRYABLLE_ERRORS = {
    ConnectionError,
    TimeoutError,
    requests.exceptions.ConnectionError,
    requests.exceptions.Timeout,
    requests.exceptions.RetryError,
    urllib3.exceptions.NewConnectionError,
    urllib3.exceptions.TimeoutError,
    urllib3.exceptions.MaxRetryError,
    elastic_transport.ConnectionError,
    elastic_transport.ConnectionTimeout,
}
