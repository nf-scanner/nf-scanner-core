"""
Interface de linha de comando para NF-Scanner-Core.
"""

import argparse
import json
import sys
from nf_scanner_core.pdf_extractor import (
    extract_text_from_pdf,
    extract_nfse_from_pdf,
    extract_and_save_nfse,
)


def main():
    """
    Execução da extração de dados de arquivos PDF de NFSe.
    """
    parser = argparse.ArgumentParser(
        description="Extrai dados de Notas Fiscais de Serviço Eletrônicas (NFSe) a partir de arquivos PDF."
    )

    parser.add_argument("pdf_path", help="Caminho para o arquivo PDF da NFSe.")

    args = parser.parse_args()

    try:

        output_path = extract_and_save_nfse(args.pdf_path)

        # Imprime os dados extraídos no formato JSON
        with open(output_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
            print(json.dumps(data, ensure_ascii=False, indent=2))

        return 0

    except Exception as e:
        print(f"Erro: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
