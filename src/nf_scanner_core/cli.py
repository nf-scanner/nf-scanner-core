"""
Interface de linha de comando simplificada para NF-Scanner-Core.

Extrai apenas CNPJ e nome do prestador de NFSe.
"""
import argparse
import json
import sys
from nf_scanner_core.pdf_extractor import extract_prestador_info, extract_and_save_prestador


def main():
    """
    Execução da extração de dados do prestador de NFSe.
    """
    parser = argparse.ArgumentParser(
        description="Extrai CNPJ e nome do prestador de NFSe a partir de arquivos PDF."
    )
    
    parser.add_argument(
        "pdf_path", 
        help="Caminho para o arquivo PDF da NFSe."
    )
    
    args = parser.parse_args()
    
    try:
        # Extrai dados do prestador
        prestador = extract_and_save_prestador(args.pdf_path)
        
        
        # Mostra um resumo
        dados = extract_prestador_info(args.pdf_path)
        print(f"CNPJ do prestador: {dados['cnpj_prestador']}")
        print(f"Nome do prestador: {dados['nome_prestador']}")
        
        return 0
        
    except Exception as e:
        print(f"Erro: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())