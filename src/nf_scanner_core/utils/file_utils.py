"""
Utilitários para manipulação de arquivos no nf-scanner-core.
"""

import os
import mimetypes
from typing import Optional, List, Tuple


def get_file_mime_type(file_path: str) -> Optional[str]:
    """
    Obtém o tipo MIME de um arquivo.

    Args:
        file_path: Caminho para o arquivo

    Returns:
        str: Tipo MIME do arquivo ou None se não for possível determinar
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"O arquivo não foi encontrado: {file_path}")

    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type


def ensure_directory_exists(directory: str) -> bool:
    """
    Garante que um diretório existe, criando-o se necessário.

    Args:
        directory: Caminho para o diretório

    Returns:
        bool: True se o diretório já existia ou foi criado com sucesso
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return os.path.isdir(directory)


def get_output_json_path(
    input_file: str, identifier: str, output_dir: Optional[str] = None
) -> str:
    """
    Gera o caminho para o arquivo JSON de saída baseado no arquivo de entrada e identificador.

    Args:
        input_file: Caminho do arquivo de entrada
        identifier: Identificador único para o arquivo (ex: código de verificação)
        output_dir: Diretório de saída opcional

    Returns:
        str: Caminho para o arquivo JSON de saída
    """
    # Define o nome do arquivo de saída
    filename = f"nfse_{identifier}.json"

    # Define o diretório de saída
    dir_path = output_dir if output_dir else os.path.dirname(input_file)

    # Cria o diretório se não existir
    ensure_directory_exists(dir_path)

    # Retorna o caminho completo
    return os.path.join(dir_path, filename)
