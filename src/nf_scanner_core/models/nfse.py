"""
Modelo principal que representa a NFSe (Nota Fiscal de Serviço Eletrônica).
"""

from dataclasses import dataclass, field
from typing import Union
from datetime import datetime

from nf_scanner_core.models.empresa import Empresa
from nf_scanner_core.models.servico_detalhe import ServicoDetalhe
from nf_scanner_core.models.valores import Valores
from nf_scanner_core.models.tributos_federais import TributosFederais


@dataclass
class NFSe:
    """
    Modelo que representa a NFSe.
    """

    # Metadados
    data_hora_emissao: datetime
    competencia: str
    codigo_verificacao: str
    numero_rps: str
    local_prestacao: str
    numero_nfse: Union[str, None]
    origem: Union[str, None]
    orgao: Union[str, None]
    nfse_substituida: Union[str, None]

    # Principais entidades
    prestador: Empresa
    tomador: Empresa

    # Detalhamento do serviço
    servico: ServicoDetalhe

    # Valores e tributos (taxas)
    valores: Valores
    tributos_federais: TributosFederais = field(default_factory=TributosFederais)

    def to_dict(self) -> dict:
        """
        Converte o objeto NFSe para um dicionário, útil para serialização em JSON.

        Returns:
            dict: Representação do NFSe em formato de dicionário
        """
        import dataclasses
        from decimal import Decimal
        from datetime import datetime

        def serialize(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            if isinstance(obj, datetime):
                return obj.isoformat()
            if dataclasses.is_dataclass(obj):
                return {k: serialize(v) for k, v in dataclasses.asdict(obj).items()}
            if isinstance(obj, (list, tuple)):
                return [serialize(item) for item in obj]
            if isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            return obj

        return serialize(self)
