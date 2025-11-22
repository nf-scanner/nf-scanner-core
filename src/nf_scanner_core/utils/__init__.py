"""
Utilitários para o nf-scanner-core.

Este módulo contém funções e classes utilitárias usadas em todo o projeto.
"""

from nf_scanner_core.utils.config import (
    get_config,
    get_ai_api_key,
    get_ai_model,
    get_ai_model_alias,
    config,
)

from nf_scanner_core.utils.ai_prompts import (
    NFSE_STRUCTURED_DATA_PROMPT,
    STRUCTURED_DATA_USER_TEXT,
    STRUCTURED_TEXT_USER_TEXT,
)

__all__ = [
    "get_config",
    "get_ai_api_key",
    "get_ai_model",
    "get_ai_model_alias",
    "config",
    "NFSE_STRUCTURED_DATA_PROMPT",
    "STRUCTURED_DATA_USER_TEXT",
    "STRUCTURED_TEXT_USER_TEXT",
]
