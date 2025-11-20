"""
Módulo de extração de texto de arquivos PDF para NF-Scanner-Core.

Este módulo fornece funcionalidades para extrair texto de arquivos PDF e armazenar os dados extraídos.
Usa PyMuPDF para extração de texto de alta performance.
"""

import os
import json
import pymupdf
from typing import Optional, Dict, Any, Union

from nf_scanner_core.models import NFSe
from nf_scanner_core.nfse_parser import NFSeParser


class PDFExtractor:
    """
    Classe responsável por extrair texto e dados estruturados de arquivos PDF.
    """
    
    def __init__(self, pdf_path: str):
        """
        Inicializa o extrator de PDF com o caminho para o arquivo PDF.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
        """
        self.pdf_path = pdf_path
        
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
            raise FileNotFoundError(f"O arquivo PDF não foi encontrado: {self.pdf_path}")

        extracted_text = ""

        try:
            doc = pymupdf.open(self.pdf_path)
            for page_num in range(len(doc)):  # Itera sobre todas as páginas do documento
                page = doc[page_num]
                extracted_text += page.get_text() + "\n"
            doc.close()

            return extracted_text.strip()

        except Exception as e:
            raise RuntimeError(f"Erro ao extrair o texto do PDF: {str(e)}")

    def _save_nfse_json(self, nfse: NFSe, output_dir: str = None) -> str:
        """
        Salva os dados estruturados da NFSe em formato JSON.

        Args:
            nfse: Objeto NFSe com dados estruturados

        Returns:
            str: Caminho do arquivo JSON salvo
        """
        # Define o caminho de saída
        filename = f"nfse_{nfse.codigo_verificacao}.json"
        dir_path = os.path.dirname(self.pdf_path)
        output_path = os.path.join(dir_path, filename)

        # Cria o diretório de saída se necessário
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

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
        
        # Converte o texto para o modelo NFSe usando o parser
        nfse = NFSeParser.parse(self._extract_text())

        # Salva os dados em formato JSON
        return self._save_nfse_json(nfse)

# Código de exemplo
if __name__ == "__main__":
    pdf_path = "./test_inputs/NFSe_ficticia_layout_completo.pdf"

    # Extrai e salva os dados da NFSe usando a nova API orientada a objetos
    extractor = PDFExtractor(pdf_path)
    json_path = extractor.extract_and_save()
    print(f"Dados da NFSe salvos em: {json_path}")