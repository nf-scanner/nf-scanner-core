"""
Interface de linha de comando para NF-Scanner-Core.
"""

import argparse
import json
import sys
import os
from nf_scanner_core import NFExtractor


def main():
    """
    Execução da extração de dados de NFSe a partir de arquivos PDF ou imagens.
    """
    parser = argparse.ArgumentParser(
        description="Extrai dados de Notas Fiscais de Serviço Eletrônicas (NFSe) a partir de arquivos PDF ou imagens."
    )

    parser.add_argument(
        "file_path", help="Caminho para o arquivo (PDF ou imagem) da NFSe."
    )
    parser.add_argument("-o", "--output", help="Caminho para o arquivo JSON de saída.")

    args = parser.parse_args()

    try:
        # Verifica se o arquivo existe
        if not os.path.exists(args.file_path):
            raise FileNotFoundError(f"O arquivo não foi encontrado: {args.file_path}")

        # Extrai e salva os dados da NFSe usando a API unificada
        extractor = NFExtractor(args.file_path, args.output)
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
