# Modulo com os tests do projeto

from .py import test_nfse_parser

from .ai import test_ai_nfse_parser
from .ai import test_extractor_modes

__all__ = [
    "test_nfse_parser",
    "test_ai_nfse_parser",
    "test_extractor_modes",
]
