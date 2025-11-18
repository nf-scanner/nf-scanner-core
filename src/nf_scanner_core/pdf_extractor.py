"""
Módulo de extração de texto de arquivos PDF para NF-Scanner-Core.

Este módulo fornece funcionalidades para extrair texto de arquivos PDF e armazenar os dados extraídos.
Usa PyMuPDF para extração de texto de alta performance.
"""
import os
import pymupdf


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
        for page_num in range(len(doc)): # Itera sobre todas as páginas do documento
            page = doc[page_num]
            extracted_text += page.get_text() + "\n"
        doc.close()
                
        return extracted_text.strip()
    
    except Exception as e:
        raise RuntimeError(f"Erro ao extrair o texto do PDF: {str(e)}")
    
if __name__ == "__main__":
    pdf_path = "./test_inputs/NFSe_ficticia_layout_completo.pdf"
    text = extract_text_from_pdf(pdf_path)
    print(text)