"""
Modelo de dados para armazenar informações básicas do prestador de NFSe.
"""
from dataclasses import dataclass
from typing import Dict


@dataclass
class PrestadorNFSe:
    """
    Modelo que representa apenas os dados do prestador de uma NFSe.
    """
    cnpj: str
    razao_social: str
    
    def to_dict(self) -> Dict[str, str]:
        """
        Converte o objeto para um dicionário, útil para serialização em JSON.
        
        Returns:
            Dict[str, str]: Representação do prestador no formato esperado
        """
        return {
            "cnpj_prestador": self.cnpj,
            "nome_prestador": self.razao_social
        }