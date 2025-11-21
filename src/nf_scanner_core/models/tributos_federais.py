"""
Modelo que representa valores dos tributos federais.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class TributosFederais:
    """Representa valores dos tributos federais."""

    pis: Decimal = Decimal("0.00")
    cofins: Decimal = Decimal("0.00")
    ir: Decimal = Decimal("0.00")
    inss: Decimal = Decimal("0.00")
    csll: Decimal = Decimal("0.00")
