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
from nf_scanner_core.parsers.nfse_parser import NFSeParser
from nf_scanner_core.parsers.ai_nfse_parser import AINFSeParser, AIParseError
from nf_scanner_core.utils.config import (
    get_ai_api_key,
    get_ai_model,
    get_ai_model_alias,
)
from nf_scanner_core.utils.file_utils import (
    get_output_json_path,
    ensure_directory_exists,
)
from nf_scanner_core.utils.ai_prompts import (
    OCR_TEXT_EXTRACTION_PROMPT,
    NFSE_STRUCTURED_DATA_PROMPT,
    OCR_USER_TEXT,
    STRUCTURED_DATA_USER_TEXT,
)

# Configuração de logging
logger = logging.getLogger(__name__)


class AIImageExtractor:
    """
    Classe para extração de texto e dados estruturados de imagens usando a API do Claude.
    """

    @staticmethod
    def _encode_image(image_path: str) -> str:
        """
        Codifica imagem em base64 para envio para a API.

        Args:
            image_path: Caminho para o arquivo de imagem

        Returns:
            String com a imagem codificada em base64

        Raises:
            FileNotFoundError: Se o arquivo de imagem não for encontrado
            IOError: Se houver um erro na leitura do arquivo
        """
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {image_path}")
            raise FileNotFoundError(f"Arquivo de imagem não encontrado: {image_path}")
        except IOError as e:
            logger.error(f"Erro ao ler o arquivo {image_path}: {str(e)}")
            raise IOError(f"Erro ao ler o arquivo de imagem: {str(e)}")

    @staticmethod
    def _get_client() -> anthropic.Anthropic:
        """
        Configura e retorna cliente da API do Claude.

        Returns:
            Cliente configurado da API Anthropic

        Raises:
            ValueError: Se a chave de API não estiver configurada
        """
        api_key = get_ai_api_key()

        if not api_key:
            error_msg = "Chave de API do Claude não configurada. Configure CLAUDE_API_KEY no arquivo .env"
            logger.error(error_msg)
            raise ValueError(error_msg)

        return anthropic.Anthropic(api_key=api_key)

    @classmethod
    def _extract_text(cls, image_path: str) -> str:
        """
        Extrai texto de uma imagem usando a API do Claude.

        Args:
            image_path: Caminho para o arquivo de imagem

        Returns:
            String com o texto extraído da imagem

        Raises:
            ValueError: Se a chave de API não estiver configurada
            Exception: Se houver um erro na extração
        """
        try:
            base64_image = cls._encode_image(image_path)

            client = cls._get_client()
            model = get_ai_model()
            model_alias = get_ai_model_alias()

            logger.info(
                f"Enviando imagem para extração de texto com Claude {model_alias}"
            )

            response = client.messages.create(
                model=model,
                max_tokens=4000,
                system=OCR_TEXT_EXTRACTION_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": OCR_USER_TEXT},
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

            extracted_text = response.content[0].text
            logger.info(f"Texto extraído com sucesso da imagem {image_path}")

            return extracted_text

        except (ValueError, FileNotFoundError, IOError) as e:
            logger.error(f"Erro na extração de texto: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Erro inesperado na extração de texto: {str(e)}")
            raise Exception(f"Erro na extração de texto da imagem: {str(e)}")

    @classmethod
    def _extract_structured_data(cls, image_path: str) -> Dict[str, Any]:
        """
        Extrai dados estruturados de uma imagem de NFSe usando a API do Claude.

        Args:
            image_path: Caminho para o arquivo de imagem de NFSe

        Returns:
            Dicionário com os dados estruturados da NFSe

        Raises:
            ValueError: Se a chave de API não estiver configurada
            Exception: Se houver um erro na extração
        """
        try:
            base64_image = cls._encode_image(image_path)

            client = cls._get_client()
            model = get_ai_model()
            model_alias = get_ai_model_alias()

            logger.info(
                f"Enviando imagem para extração de dados estruturados com Claude {model_alias}"
            )

            response = client.messages.create(
                model=model,
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
                    f"Dados estruturados extraídos com sucesso da imagem {image_path}"
                )
                return AINFSeParser._converter_para_modelos(result)
            except json.JSONDecodeError as e:
                raise AIParseError(
                    f"Erro ao fazer o parsing do JSON retornado pelo Claude: {str(e)}"
                )

        except (ValueError, FileNotFoundError, IOError, AIParseError) as e:
            logger.error(f"Erro na extração de dados estruturados: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Erro inesperado na extração de dados estruturados: {str(e)}")
            raise Exception(
                f"Erro na extração de dados estruturados da imagem: {str(e)}"
            )

    @classmethod
    def _process_image_file(
        cls,
        image_path: str,
        output_dir: Optional[str] = None,
        structured_data: bool = True,
    ) -> str | NFSe:
        """
        Processa um arquivo de imagem de NFSe, extraindo texto e dados estruturados.

        Args:
            image_path: Caminho para o arquivo de imagem
            output_dir: Diretório de saída (opcional)
            structured_data: Se True, extrai texto bruto; se False, extrai e estrutura como NFSe

        Returns:
            str: texto extraído da imagem (se structured_data=True)
            NFSe: objeto NFSe com os dados extraídos (se structured_data=False)

        Raises:
            FileNotFoundError: Se o arquivo de imagem não for encontrado
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Arquivo de imagem não encontrado: {image_path}")

        if not structured_data:
            extracted_text = cls._extract_text(image_path)
            return extracted_text

        # Tenta extrair e estruturar como NFSe
        nfse = None
        try:
            nfse = cls._extract_structured_data(image_path)

            if output_dir:
                ensure_directory_exists(output_dir)
                json_path = get_output_json_path(image_path, output_dir)

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(nfse.to_dict(), f, ensure_ascii=False, indent=4)

                logger.info(f"Dados extraídos salvos em {json_path}")

        except Exception as e:
            logger.error(f"Erro ao extrair dados estruturados: {str(e)}")
            raise e

        return nfse

    @classmethod
    def extract_and_save(
        cls,
        image_path: str,
        output_dir: Optional[str] = None,
        structured_data: bool = True,
    ) -> str:
        """
        Extrai dados de uma NFSe a partir de uma imagem

        Args:
            image_path: Caminho para o arquivo de imagem
            output_dir: Diretório de saída (opcional)
            structured_data: Se True, extrai texto bruto; se False, extrai e estrutura como NFSe
        Returns:
            str: Caminho do arquivo JSON salvo
        """
        return cls._process_image_file(image_path, output_dir, structured_data)
