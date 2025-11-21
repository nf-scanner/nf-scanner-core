"""
Modelo que representa um endereço.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Endereco:
    """Representa um endereço completo."""

    logradouro: str
    numero: str
    bairro: Optional[str] = None
    cep: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None

    def __str__(self) -> str:
        partes = [f"{self.logradouro}, {self.numero}"]
        if self.bairro:
            partes.append(f"- {self.bairro}")
        if self.cep:
            partes.append(f"- CEP: {self.cep}")
        if self.municipio and self.uf:
            partes.append(f"- {self.municipio}/{self.uf}")
        return " ".join(partes)
