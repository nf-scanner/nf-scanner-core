"""
Modelo que representa detalhes do serviço prestado.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ServicoDetalhe:
    """Representa detalhes do serviço prestado."""

    descricao: str
    codigo_servico: Optional[str] = None
    atividade_descricao: Optional[str] = None
    cnae: Optional[str] = None
    cnae_descricao: Optional[str] = None
    observacoes: Optional[str] = None
