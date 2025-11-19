"""
Modelo de dados para armazenar informações extraídas de Notas Fiscais de Serviço Eletrônicas (NFSe).
"""

from dataclasses import dataclass, field
from typing import Optional, List, Union
from decimal import Decimal
from datetime import datetime


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


@dataclass
class Contato:
    """Representa informações de contato."""

    telefone: Optional[str] = None
    email: Optional[str] = None


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


@dataclass
class ServicoDetalhe:
    """Representa detalhes do serviço prestado."""

    descricao: str
    codigo_servico: Optional[str] = None
    atividade_descricao: Optional[str] = None
    cnae: Optional[str] = None
    cnae_descricao: Optional[str] = None
    observacoes: Optional[str] = None


@dataclass
class ConstrucaoCivil:
    """Representa detalhes específicos de construção civil."""

    codigo_obra: Optional[str] = None
    codigo_art: Optional[str] = None


@dataclass
class TributosFederais:
    """Representa valores dos tributos federais."""

    pis: Decimal = Decimal("0.00")
    cofins: Decimal = Decimal("0.00")
    ir: Decimal = Decimal("0.00")
    inss: Decimal = Decimal("0.00")
    csll: Decimal = Decimal("0.00")


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
        import json
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
