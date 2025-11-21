#!/usr/bin/env python3
"""
Exemplo básico de uso da biblioteca nf-scanner-core.

Este exemplo demonstra como usar a classe principal NFExtractor para
extrair dados de uma NFSe a partir de um arquivo PDF ou imagem.
"""

from nf_scanner_core import NFExtractor


def extract_from_pdf():
    """Exemplo de extração a partir de um PDF."""
    # Cria o extrator para um arquivo PDF
    extractor = NFExtractor("./test_inputs/NFSe_ficticia_layout_completo.pdf")

    # Extrai e salva os dados
    json_path = extractor.extract_and_save()
    print(f"Dados da NFSe (PDF) salvos em: {json_path}")

    # Também podemos extrair sem salvar
    nfse = extractor.extract()
    print(f"Número da NFSe: {nfse.numero}")
    print(f"Valor total: {nfse.valor_total}")


def extract_from_image():
    """Exemplo de extração a partir de uma imagem."""
    # Cria o extrator para um arquivo de imagem
    extractor = NFExtractor("./test_inputs/NFSe_ficticia_layout_completo.jpg")

    # Extrai e salva os dados
    json_path = extractor.extract_and_save()
    print(f"Dados da NFSe (imagem) salvos em: {json_path}")


def extract_with_custom_output():
    """Exemplo de extração com diretório de saída personalizado."""
    # Cria o extrator com um diretório de saída personalizado
    extractor = NFExtractor(
        "./test_inputs/NFSe_ficticia_layout_completo.pdf", output_dir="./output"
    )

    # Extrai e salva os dados
    json_path = extractor.extract_and_save()
    print(f"Dados da NFSe salvos em: {json_path}")


if __name__ == "__main__":
    print("=== Exemplo de extração a partir de um PDF ===")
    extract_from_pdf()

    print("\n=== Exemplo de extração a partir de uma imagem ===")
    extract_from_image()

    print("\n=== Exemplo de extração com diretório de saída personalizado ===")
    extract_with_custom_output()
