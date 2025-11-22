"""
Módulo de extração de texto de arquivos PDF para NF-Scanner-Core.

Este módulo fornece a interface para extrair texto de arquivos PDF utilizando PyMuPDF.
"""

import os
import pymupdf

from nf_scanner_core.models import NFSe
from nf_scanner_core.parsers.nfse_parser import NFSeParser
from nf_scanner_core.parsers.ai_nfse_parser import AINFSeParser


class PDFExtractor:
    """
    Classe responsável por extrair texto e dados estruturados de arquivos PDF.
    """

    def __init__(self, pdf_path: str, ai_parse: bool = False):
        """
        Inicializa o extrator de PDF com o caminho para o arquivo PDF.

        Args:
            pdf_path: Caminho para o arquivo PDF
        """
        self.pdf_path = pdf_path
        self.ai_parse = ai_parse

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

    def extract(self) -> NFSe:
        """
        Extrai dados de uma NFSe a partir de um PDF e salva em formato JSON.

        Returns:
            NFSe: Objeto NFSe com os dados extraídos
        """
        text = self._extract_text()
        if self.ai_parse:
            return AINFSeParser.parse(text)
        else:
            return NFSeParser.parse(text)
