"""
Módulo de extração de texto de arquivos PDF para NF-Scanner-Core.

Este módulo fornece funcionalidades para extrair dados básicos de uma NFSe a partir de um arquivo PDF.
"""
import os
import pymupdf
from typing import Dict

from nf_scanner_core.nfse_parser import extrair_dados_basicos_nfse
from nf_scanner_core.models import PrestadorNFSe


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


def extract_prestador_info(pdf_path: str) -> Dict[str, str]:
    """
    Extrai apenas o CNPJ e nome do prestador de um PDF de NFSe.
    
    Args:
        pdf_path: Caminho para o arquivo PDF da NFSe
        
    Returns:
        Dict[str, str]: Dicionário com cnpj_prestador e nome_prestador
        
    Raises:
        FileNotFoundError: Se o arquivo PDF não for encontrado
        RuntimeError: Se houver um erro ao processar o arquivo PDF
    """
    # Extrai o texto do PDF
    texto = extract_text_from_pdf(pdf_path)
    
    # Extrai os dados básicos do prestador
    return extrair_dados_basicos_nfse(texto)


def save_prestador_json(dados: Dict[str, str]) -> PrestadorNFSe:
    """
    Salva os dados do prestador em formato JSON.
    
    Args:
        dados: Dicionário com dados do prestador
        
    Returns:
        PrestadorNFSe: Objeto com os dados do prestador
    """
    return PrestadorNFSe(cnpj=dados["cnpj_prestador"], razao_social=dados["nome_prestador"])


def extract_and_save_prestador(pdf_path: str) -> PrestadorNFSe:
    """
    Extrai dados do prestador a partir de um PDF e salva em formato JSON.
    
    Args:
        pdf_path: Caminho para o arquivo PDF da NFSe
        
    Returns:
        PrestadorNFSe: Objeto com os dados do prestador
    """
    # Extrai dados do prestador
    dados = extract_prestador_info(pdf_path)
    
    # Salva os dados em formato JSON
    return save_prestador_json(dados)


if __name__ == "__main__":
    pdf_path = "./test_inputs/NFSe_ficticia_layout_completo.pdf"
    
    # Extrai e salva os dados do prestador
    resultado = extract_and_save_prestador(pdf_path)
    print(f"Dados do prestador: {resultado}")
    