"""
Modelo que representa informações de contato.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Contato:
    """Representa informações de contato."""

    telefone: Optional[str] = None
    email: Optional[str] = None
