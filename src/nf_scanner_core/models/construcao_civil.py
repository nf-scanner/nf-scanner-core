"""
Modelo que representa detalhes específicos de construção civil.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ConstrucaoCivil:
    """Representa detalhes específicos de construção civil."""

    codigo_obra: Optional[str] = None
    codigo_art: Optional[str] = None
