"""
Módulo de configuração e gerenciamento de variáveis de ambiente.

Este módulo fornece funções para carregar e acessar configurações
a partir de arquivos .env do projeto.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv


class Config:
    """
    Classe responsável por gerenciar configurações e variáveis de ambiente.

    Carrega configurações de arquivos .env do projeto.
    Fornece acesso centralizado às configurações da aplicação.
    """

    _instance = None
    _is_initialized = False
    _config_values: Dict[str, Any] = {}

    def __new__(cls):
        """Implementação de singleton para garantir uma única instância da configuração."""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializa a configuração carregando o arquivo .env se ainda não tiver sido inicializado."""
        if not Config._is_initialized:
            self._load_env_file()
            Config._is_initialized = True

    def _load_env_file(self, env_path: Optional[str] = None) -> None:
        """
        Carrega as variáveis de ambiente de um arquivo .env.

        Args:
            env_path: Caminho opcional para o arquivo .env.
                     Se não for fornecido, tenta localizar o arquivo automaticamente.
        """
        if env_path:
            env_file = Path(env_path)
        else:
            # Tenta encontrar o arquivo .env em vários locais
            # 1. No diretório atual
            # 2. No diretório do projeto (um nível acima se estivermos em src/)
            possible_paths = [
                Path(".env"),  # Diretório atual
                Path(__file__).parents[3] / ".env",  # Raiz do projeto
            ]

            env_file = next((path for path in possible_paths if path.exists()), None)

        # Carrega as variáveis do arquivo .env, se encontrado
        if env_file and env_file.exists():
            load_dotenv(dotenv_path=str(env_file), override=True)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtém uma configuração pelo nome.

        Verifica primeiro as configurações carregadas, depois as variáveis de ambiente.

        Args:
            key: Nome da configuração
            default: Valor padrão caso a configuração não exista

        Returns:
            Valor da configuração ou o valor padrão
        """
        # Verifica se está no cache de configurações
        if key in self._config_values:
            return self._config_values[key]

        # Verifica nas variáveis de ambiente
        value = os.environ.get(key, default)

        # Armazena no cache
        self._config_values[key] = value

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Define uma configuração em tempo de execução.

        Args:
            key: Nome da configuração
            value: Valor da configuração
        """
        self._config_values[key] = value

    def get_ai_api_key(self) -> Optional[str]:
        """
        Obtém a chave de API para integração com o modelo de IA.

        Returns:
            Chave de API para o modelo de IA ou None se não estiver configurada
        """
        return self.get("CLAUDE_API_KEY")

    def get_ai_model(self) -> str:
        """
        Obtém o modelo a ser utilizado.

        Returns:
            Nome do modelo
        """
        return self.get("CLAUDE_API_ID", "claude-sonnet-4-5-20250929")

    def get_ai_model_alias(self) -> str:
        """
        Obtém o alias do modelo.

        Returns:
            Alias do modelo
        """
        return self.get("CLAUDE_API_ALIAS", "claude-sonnet-4-5")


# Instância global da configuração para fácil acesso
config = Config()


# Funções para acessar as configurações
def get_config(key: str, default: Any = None) -> Any:
    """
    Obtém uma configuração pelo nome.

    Args:
        key: Nome da configuração
        default: Valor padrão caso a configuração não exista

    Returns:
        Valor da configuração ou o valor padrão
    """
    return config.get(key, default)


def get_ai_api_key() -> Optional[str]:
    """
    Obtém a chave de API para integração com o modelo de IA.

    Returns:
        Chave de API para o modelo de IA ou None se não estiver configurada
    """
    return config.get_ai_api_key()


def get_ai_model() -> str:
    """
    Obtém o modelo a ser utilizado.

    Returns:
        Nome do modelo
    """
    return config.get_ai_model()


def get_ai_model_alias() -> str:
    """
    Obtém o alias do modelo.

    Returns:
        Alias do modelo
    """
    return config.get_ai_model_alias()
