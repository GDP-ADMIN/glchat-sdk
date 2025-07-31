"""Constants.

Authors:
    Ryan Ignatius Hadiwijaya (ryan.i.hadiwijaya@gdplabs.id)

References:
    None
"""

import os

from dotenv import load_dotenv

load_dotenv()

LM_INVOKER_TIMEOUT_SECONDS = int(os.getenv("LM_INVOKER_TIMEOUT_SECONDS", "300"))
LM_INVOKER_MAX_RETRIES = int(os.getenv("LM_INVOKER_MAX_RETRIES", "2"))
