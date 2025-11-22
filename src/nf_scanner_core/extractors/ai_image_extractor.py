"""
Módulo de extração de texto de arquivos de imagem usando IA.

Este módulo fornece uma interface para extrair texto e dados estruturados de arquivos de imagem utilizando
o Claude.
"""

import os
import json
import base64
import logging
from typing import Optional, Dict, Any, Union, Tuple
from pathlib import Path

import anthropic
from PIL import Image

from nf_scanner_core.models import NFSe
from nf_scanner_core.parsers.ai_nfse_parser import AINFSeParser, AIParseError
from nf_scanner_core.utils.config import (
    get_ai_api_key,
    get_ai_model,
    get_ai_model_alias,
)
from nf_scanner_core.utils.ai_prompts import (
    NFSE_STRUCTURED_DATA_PROMPT,
    STRUCTURED_DATA_USER_TEXT,
)

# Configuração de logging
logger = logging.getLogger(__name__)


class AIImageExtractor:
    """
    Classe para extração de texto e dados estruturados de imagens usando a API do Claude.
    """

    def __init__(self, image_path: str):
        """
        Inicializa o extrator de imagem com IA com o caminho para o arquivo de imagem.

        Args:
            image_path: Caminho para o arquivo de imagem
        """
        self.image_path = image_path
        self.api_key = get_ai_api_key()
        self.model = get_ai_model()
        self.model_alias = get_ai_model_alias()

        if not self.api_key:
            error_msg = "Chave de API do Claude não configurada. Configure CLAUDE_API_KEY no arquivo .env"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _encode_image(self) -> str:
        """
        Codifica imagem em base64 para envio para a API.

        Returns:
            String com a imagem codificada em base64

        Raises:
            IOError: Se houver um erro na leitura do arquivo
        """
        try:
            with open(self.image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except IOError as e:
            logger.error(f"Erro ao ler o arquivo {self.image_path}: {str(e)}")
            raise IOError(f"Erro ao ler o arquivo de imagem: {str(e)}")

    def _get_client(self) -> anthropic.Anthropic:
        """
        Retorna cliente da API do Claude.

        Returns:
            Cliente configurado da API Anthropic
        """
        return anthropic.Anthropic(api_key=self.api_key)

    def _extract_structured_data(self) -> NFSe:
        """
        Extrai dados estruturados de uma imagem de NFSe usando a API do Claude.

        Returns:
            Objeto NFSe com os dados estruturados extraídos

        Raises:
            Exception: Se houver um erro na extração
        """
        try:
            base64_image = self._encode_image()
            client = self._get_client()

            logger.info(
                f"Enviando imagem para extração de dados estruturados com Claude {self.model_alias}"
            )

            response = client.messages.create(
                model=self.model,
                max_tokens=4000,
                system=NFSE_STRUCTURED_DATA_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": STRUCTURED_DATA_USER_TEXT},
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image,
                                },
                            },
                        ],
                    }
                ],
            )

            content = response.content[0].text
            content = content.replace("```json", "").replace("```", "").strip()

            try:
                result = json.loads(content)
                logger.info(
                    f"Dados estruturados extraídos com sucesso da imagem {self.image_path}"
                )
                return AINFSeParser._converter_para_modelos(result)
            except json.JSONDecodeError as e:
                raise AIParseError(
                    f"Erro ao fazer o parsing do JSON retornado pelo Claude: {str(e)}"
                )

        except (ValueError, IOError, AIParseError) as e:
            logger.error(f"Erro na extração de dados estruturados: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Erro inesperado na extração de dados estruturados: {str(e)}")
            raise Exception(
                f"Erro na extração de dados estruturados da imagem: {str(e)}"
            )

    def extract(self) -> NFSe:
        """
        Extrai dados de uma NFSe a partir de uma imagem usando a API do Claude.

        Returns:
            NFSe: objeto NFSe com os dados extraídos
        """
        return self._extract_structured_data()
