"""
Módulo de extração de texto de arquivos PDF para NF-Scanner-Core.

Este módulo fornece a interface para extrair texto de arquivos PDF utilizando PyMuPDF.
"""

import os
import json
import pymupdf
from typing import Optional, Dict, Any, Union

from nf_scanner_core.models import NFSe
from nf_scanner_core.parsers.nfse_parser import NFSeParser
from nf_scanner_core.utils.file_utils import (
    get_output_json_path,
    ensure_directory_exists,
)


class PDFExtractor:
    """
    Classe responsável por extrair texto e dados estruturados de arquivos PDF.
    """

    def __init__(self, pdf_path: str, output_dir: Optional[str] = None):
        """
        Inicializa o extrator de PDF com o caminho para o arquivo PDF.

        Args:
            pdf_path: Caminho para o arquivo PDF
            output_dir: Diretório de saída opcional para salvar os resultados
        """
        self.pdf_path = pdf_path
        self.output_dir = output_dir

    def _extract_text(self) -> str:
        """
        Extrai o texto de um arquivo PDF usando PyMuPDF.

        Returns:
            str: Texto extraído do arquivo PDF

        Raises:
            FileNotFoundError: Se o arquivo PDF não for encontrado
            RuntimeError: Se houver um erro ao ler o arquivo PDF
        """
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(
                f"O arquivo PDF não foi encontrado: {self.pdf_path}"
            )

        extracted_text = ""

        try:
            doc = pymupdf.open(self.pdf_path)
            for page_num in range(
                len(doc)
            ):  # Itera sobre todas as páginas do documento
                page = doc[page_num]
                extracted_text += page.get_text() + "\n"
            doc.close()

            return extracted_text.strip()

        except Exception as e:
            raise RuntimeError(f"Erro ao extrair o texto do PDF: {str(e)}")

    def _save_nfse_json(self, nfse: NFSe) -> str:
        """
        Salva os dados estruturados da NFSe em formato JSON.

        Args:
            nfse: Objeto NFSe com dados estruturados

        Returns:
            str: Caminho do arquivo JSON salvo
        """
        # Define o caminho de saída
        output_path = get_output_json_path(
            self.pdf_path, nfse.codigo_verificacao, self.output_dir
        )

        # Converte o objeto NFSe para um dicionário
        nfse_dict = nfse.to_dict()

        # Cria resposta no formato de API HTTP
        response = {"status": "success", "code": 200, "data": {"nfse": nfse_dict}}

        # Salva o JSON
        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(response, json_file, indent=2, ensure_ascii=False)

        return output_path

    def extract_and_save(self) -> str:
        """
        Extrai dados de uma NFSe a partir de um PDF e salva em formato JSON.

        Returns:
            str: Caminho do arquivo JSON salvo
        """
        # Extrai texto do PDF
        text = self._extract_text()

        # Converte o texto para o modelo NFSe usando o parser
        nfse = NFSeParser.parse(text)

        # Salva os dados em formato JSON
        return self._save_nfse_json(nfse)
