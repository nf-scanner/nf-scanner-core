"""
Testes para os diferentes modos de extração e parsing de NFSe.

Este módulo testa as diferentes combinações de extração e parsing:
1. Extração regular (sem IA)
2. Extração com IA
3. Parsing com IA
4. Combinações de modos
"""

import os
import json
import pytest
from decimal import Decimal

from nf_scanner_core.extractor import NFExtractor
from nf_scanner_core.models import NFSe
from nf_scanner_core.utils.config import get_ai_api_key

# Caminhos para os arquivos de teste
IMAGE_PATH = os.path.join("test_inputs", "NFSe_ficticia_layout_completo.jpg")
PDF_PATH = os.path.join("test_inputs", "NFSe_ficticia_layout_completo.pdf")


@pytest.fixture
def has_claude_api_key():
    """Verifica se a chave de API do Claude está configurada."""
    api_key = get_ai_api_key()
    if not api_key:
        pytest.skip("Chave de API do Claude não configurada. Pulando testes de IA.")
    return api_key is not None


def test_regular_extraction_image():
    """
    Testa a extração e parsing padrão (sem IA) de uma imagem.
    """
    extractor = NFExtractor(IMAGE_PATH)
    nfse = extractor.extract()

    assert isinstance(nfse, NFSe)
    assert nfse.numero_nfse == "29"
    assert nfse.prestador.razao_social == "EMPRESA FICTÍCIA LTDA"
    assert nfse.tomador.cnpj == "98.765.432/0001-55"


def test_regular_extraction_pdf():
    """
    Testa a extração e parsing padrão (sem IA) de um PDF.
    """
    extractor = NFExtractor(PDF_PATH)
    nfse = extractor.extract()

    assert isinstance(nfse, NFSe)
    assert nfse.numero_nfse == "29"
    assert nfse.prestador.razao_social == "EMPRESA FICTÍCIA LTDA"
    assert nfse.tomador.razao_social == "CLIENTE TESTE S.A."
    assert nfse.valores.valor_servicos == Decimal("1500.00")


@pytest.mark.skipif(
    not get_ai_api_key(), reason="Chave de API do Claude não configurada"
)
def test_ai_extraction_image():
    """
    Testa a extração usando IA para uma imagem.
    """
    extractor = NFExtractor(IMAGE_PATH, ai_extraction=True)
    nfse = extractor.extract()

    assert isinstance(nfse, NFSe)
    assert nfse.numero_nfse == "29"
    assert nfse.prestador.razao_social == "EMPRESA FICTÍCIA LTDA"
    assert nfse.codigo_verificacao == "XYZ123"
    assert nfse.prestador.inscricao_municipal == "123456"
    assert nfse.tomador.inscricao_estadual == "888888"
    assert nfse.valores.valor_servicos == Decimal("1500.00")
    assert nfse.valores.aliquota == Decimal("0.02")


@pytest.mark.skipif(
    not get_ai_api_key(), reason="Chave de API do Claude não configurada"
)
def test_ai_parse_image():
    """
    Testa o parsing usando IA de uma imagem extraída com OCR tradicional.
    """
    extractor = NFExtractor(IMAGE_PATH, ai_parse=True)
    nfse = extractor.extract()

    assert isinstance(nfse, NFSe)
    assert nfse.numero_nfse == "29"
    assert nfse.prestador.razao_social == "EMPRESA FICTÍCIA LTDA"
    assert "SECRETARIA MUNICIPAL DE ADMINISTRAÇÃO E FINANÇAS" in nfse.orgao.upper()
    assert nfse.valores.valor_servicos == Decimal("1500.00")
    assert nfse.valores.aliquota == Decimal("0.02")


@pytest.mark.skipif(
    not get_ai_api_key(), reason="Chave de API do Claude não configurada"
)
def test_ai_parse_pdf():
    """
    Testa o parsing usando IA de um PDF extraído com PyMuPDF.
    """
    extractor = NFExtractor(PDF_PATH, ai_parse=True)
    nfse = extractor.extract()

    assert isinstance(nfse, NFSe)
    assert nfse.numero_nfse == "29"
    assert nfse.prestador.razao_social == "EMPRESA FICTÍCIA LTDA"
    assert nfse.codigo_verificacao == "XYZ123"
    assert nfse.tomador.cnpj == "98.765.432/0001-55"
    assert nfse.tomador.inscricao_estadual == "888888"
    assert nfse.valores.valor_servicos == Decimal("1500.00")
    assert nfse.servico.codigo_servico == "14.01"


@pytest.mark.skipif(
    not get_ai_api_key(), reason="Chave de API do Claude não configurada"
)
def test_ai_extraction_pdf_error():
    """
    Testa que a extração usando IA para PDF gera um erro ou aviso apropriado.
    O sistema deve rejeitar esse tipo de operação, pois a extração de PDF com PyMuPDF já é eficiente.
    """
    with pytest.raises(Exception, match="IA para extração de PDF não é eficiente"):
        extractor = NFExtractor(PDF_PATH, ai_extraction=True)
        extractor.extract()


def test_data_quality_comparison():
    """
    Testa e compara a qualidade dos dados extraídos usando diferentes métodos.
    Este teste é mais informativo do que assertivo, mostrando as diferenças entre os métodos.
    """
    if not get_ai_api_key():
        pytest.skip("Chave de API do Claude não configurada.")

    # Extração regular
    regular_extractor = NFExtractor(IMAGE_PATH)
    regular_nfse = regular_extractor.extract()

    # Extração com IA
    ai_extraction_extractor = NFExtractor(IMAGE_PATH, ai_extraction=True)
    ai_extraction_nfse = ai_extraction_extractor.extract()

    # Extração regular com parsing IA
    ai_parse_extractor = NFExtractor(IMAGE_PATH, ai_parse=True)
    ai_parse_nfse = ai_parse_extractor.extract()

    # Campos onde esperamos que a IA seja melhor
    expected_better_fields = [
        "prestador.razao_social",
        "prestador.email",
        "servico.descricao",
        "tomador.razao_social",
        "valores.valor_servicos",
    ]

    # Para fins de documentação/logging, não verificamos diretamente
    for field in expected_better_fields:
        parts = field.split(".")
        if len(parts) == 2:
            entity, attr = parts
            regular_value = getattr(getattr(regular_nfse, entity), attr, None)
            ai_extraction_value = getattr(
                getattr(ai_extraction_nfse, entity), attr, None
            )
            ai_parse_value = getattr(getattr(ai_parse_nfse, entity), attr, None)

            print(f"\nField: {field}")
            print(f"Regular extraction: {regular_value}")
            print(f"AI extraction: {ai_extraction_value}")
            print(f"AI parsing: {ai_parse_value}")

    # Verificamos que os valores monetários são extraídos corretamente com IA
    assert ai_extraction_nfse.valores.valor_servicos > Decimal("0")
    assert ai_parse_nfse.valores.valor_servicos > Decimal("0")
