"""
Modelo que representa valores financeiros da nota fiscal.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Valores:
    """Representa valores financeiros da nota fiscal."""

    valor_servicos: Decimal
    desconto: Decimal = Decimal("0.00")
    valor_liquido: Decimal = Decimal("0.00")
    base_calculo: Decimal = Decimal("0.00")
    aliquota: Decimal = Decimal("0.00")
    valor_iss: Decimal = Decimal("0.00")
    outras_retencoes: Decimal = Decimal("0.00")
    retencoes_federais: Decimal = Decimal("0.00")
