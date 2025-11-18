"""
Interface de linha de comando para NF-Scanner-Core.
"""
import argparse
from nf_scanner_core.pdf_extractor import extract_text_from_pdf


def main():
    """
    Execução da extração de texto de arquivos PDF.
    """
    parser = argparse.ArgumentParser(description="Extrai texto de arquivos PDF.")
    parser.add_argument(
        "pdf_path", 
        help="Caminho para o arquivo PDF de onde extrair o texto."
    )
    
    args = parser.parse_args()
    
    try:
        output_path = extract_text_from_pdf(args.pdf_path)
        print(output_path)
    except Exception as e:
        print(f"Erro: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    main()
