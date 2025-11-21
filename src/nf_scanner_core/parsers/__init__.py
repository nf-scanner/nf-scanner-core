"""
Módulo de parsers para NF-Scanner-Core.

Este módulo contém os parsers para diferentes tipos de documentos fiscais.
"""

from nf_scanner_core.parsers.nfse_parser import NFSeParser
from nf_scanner_core.parsers.ai_nfse_parser import AINFSeParser

__all__ = ["NFSeParser", "AINFSeParser"]
