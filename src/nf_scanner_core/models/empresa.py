"""
Modelo que representa uma empresa (prestador ou tomador de serviço).
"""

from dataclasses import dataclass
from typing import Optional

from nf_scanner_core.models.endereco import Endereco
from nf_scanner_core.models.contato import Contato


@dataclass
class Empresa:
    """Representa informações de uma empresa (prestador ou tomador)."""

    razao_social: str
    cnpj: str
    inscricao_municipal: Optional[str] = None
    inscricao_estadual: Optional[str] = None
    nome_fantasia: Optional[str] = None
    endereco: Optional[Endereco] = None
    contato: Optional[Contato] = None
