"""Defines a logger for logging.

Example of Displayed Logs using default format:
[16/04/2025 15:08:18.323 GDPLabsGenAILogger INFO] Loading prompt_builder catalog for chatbot `general-purpose`

Authors:
    Pray Somaldo (pray.somaldo@gdplabs.id)
    Anggara Setiawan (anggara.t.setiawan@gdplabs.id)
    Hermes Vincentius Gani (hermes.v.gani@gdplabs.id)

References:
    [1] https://github.com/GDP-ADMIN/gsdp
"""

from gllm_core.utils.logger_manager import  LoggerManager

LOGGER_NAME = "GDPLabsGenAILogger"

logger = LoggerManager.get_logger(LOGGER_NAME)
