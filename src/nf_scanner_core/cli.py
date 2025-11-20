"""
Interface de linha de comando para NF-Scanner-Core.
"""

import argparse
import json
import sys
from nf_scanner_core.pdf_extractor import PDFExtractor


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
        # Extrai e salva os dados da NFSe usando a nova API orientada a objetos
        extractor = PDFExtractor(args.pdf_path)
        output_path = extractor.extract_and_save()

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