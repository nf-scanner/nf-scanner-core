"""
Interface de linha de comando para NF-Scanner-Core.
"""

import argparse
import sys
import os
from nf_scanner_core import NFExtractor
import json


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
    parser.add_argument(
        "-aiextract",
        "--ai-extraction",
        action="store_true",
        help="Usa IA para extração.",
    )
    parser.add_argument(
        "-aiparse",
        "--ai-parse",
        action="store_true",
        help="Usa IA para parsear os dados.",
    )

    args = parser.parse_args()

    try:
        # Verifica se o arquivo existe
        if not os.path.exists(args.file_path):
            raise FileNotFoundError(f"O arquivo não foi encontrado: {args.file_path}")

        # Extrai e salva os dados da NFSe usando a API unificada
        extractor = NFExtractor(args.file_path, args.ai_extraction, args.ai_parse)
        nfse = extractor.extract()
        print(json.dumps(nfse.to_dict(), indent=2, ensure_ascii=False))

        return 0

    except Exception as e:
        print(f"Erro: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
