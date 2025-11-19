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
from nf_scanner_core.nfse_parser import texto_para_nfse


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrai o texto de um arquivo PDF usando PyMuPDF.

    Args:
        pdf_path: Caminho para o arquivo PDF

    Returns:
        str: Texto extraído do arquivo PDF

    Raises:
        FileNotFoundError: Se o arquivo PDF não for encontrado
        RuntimeError: Se houver um erro ao ler o arquivo PDF
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"O arquivo PDF não foi encontrado: {pdf_path}")

    extracted_text = ""

    try:
        doc = pymupdf.open(pdf_path)
        for page_num in range(len(doc)):  # Itera sobre todas as páginas do documento
            page = doc[page_num]
            extracted_text += page.get_text() + "\n"
        doc.close()

        return extracted_text.strip()

    except Exception as e:
        raise RuntimeError(f"Erro ao extrair o texto do PDF: {str(e)}")


def extract_nfse_from_pdf(pdf_path: str) -> NFSe:
    """
    Extrai dados estruturados de uma NFSe a partir de um arquivo PDF.

    Args:
        pdf_path: Caminho para o arquivo PDF da NFSe

    Returns:
        NFSe: Objeto com dados estruturados da NFSe

    Raises:
        FileNotFoundError: Se o arquivo PDF não for encontrado
        RuntimeError: Se houver um erro ao processar o arquivo PDF
    """
    # Extrai o texto do PDF
    texto = extract_text_from_pdf(pdf_path)

    print(texto)
    # Converte o texto para o modelo NFSe
    return texto_para_nfse(texto)


def save_nfse_json(nfse: NFSe) -> str:
    """
    Salva os dados estruturados da NFSe em formato JSON.

    Args:
        nfse: Objeto NFSe com dados estruturados

    Returns:
        str: Caminho do arquivo JSON salvo
    """

    output_path = f"nfse_{nfse.codigo_verificacao}.json"

    # Converte o objeto NFSe para um dicionário
    nfse_dict = nfse.to_dict()

    # Cria resposta no formato de API HTTP
    response = {"status": "success", "code": 200, "data": {"nfse": nfse_dict}}

    # Salva o JSON
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(response, json_file, indent=2, ensure_ascii=False)

    return output_path


def extract_and_save_nfse(pdf_path: str) -> str:
    """
    Extrai dados de uma NFSe a partir de um PDF e salva em formato JSON.

    Args:
        pdf_path: Caminho para o arquivo PDF da NFSe

    Returns:
        str: Caminho do arquivo JSON salvo
    """
    # Extrai dados estruturados da NFSe
    nfse = extract_nfse_from_pdf(pdf_path)

    # Salva os dados em formato JSON
    return save_nfse_json(nfse)


if __name__ == "__main__":
    pdf_path = "./test_inputs/NFSe_ficticia_layout_completo.pdf"

    # Extrai e salva os dados da NFSe
    json_path = extract_and_save_nfse(pdf_path)
    print(f"Dados da NFSe salvos em: {json_path}")
