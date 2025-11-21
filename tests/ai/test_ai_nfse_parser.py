"""
Testes para o módulo de parser AI da NFSe.
"""

import os
import json
import pytest
from decimal import Decimal
from datetime import datetime

from nf_scanner_core.models import NFSe
from nf_scanner_core.parsers.nfse_parser import NFSeParser
from nf_scanner_core.parsers.ai_nfse_parser import AINFSeParser, AIParseError
from nf_scanner_core.utils.config import get_ai_api_key

from ..py.test_nfse_parser import TEXTO_NFSE_EXEMPLO


@pytest.fixture
def has_claude_api_key():
    """Verifica se a chave de API do Claude está configurada."""
    api_key = get_ai_api_key()
    if not api_key:
        pytest.skip("Chave de API do Claude não configurada. Pulando testes de IA.")
    return api_key is not None


@pytest.fixture(scope="module")
def parsed_nfse():
    """
    Executa o parser AI e retorna o resultado para reutilização nos testes, evitando custos de API desnecessários.

    O escopo "module" garante que a função será executada apenas uma vez por módulo.
    """
    if not get_ai_api_key():
        pytest.skip("Chave de API do Claude não configurada. Pulando testes de IA.")

    try:
        # Executa o parser apenas uma vez
        return AINFSeParser.parse(TEXTO_NFSE_EXEMPLO)
    except AIParseError as e:
        pytest.skip(f"Erro no parsing com IA: {str(e)}")


def test_AI_NFSe_parser(parsed_nfse):
    """
    Testa o parser AI.
    """
    nfse = parsed_nfse

    assert isinstance(nfse, NFSe)

    # 1. Testa dados de cabeçalho
    assert nfse.data_hora_emissao.strftime("%d/%m/%Y %H:%M") == "01/01/2025 09:00"
    assert nfse.competencia.lower() == "01/2025".lower()
    assert nfse.codigo_verificacao.lower() == "XYZ123".lower()
    assert nfse.numero_rps.lower() == "000045".lower()
    assert nfse.local_prestacao.lower() == "CIDADE EXEMPLO".lower()
    assert nfse.numero_nfse.lower() == "29".lower()
    assert "prefeitura municipal de cidade exemplo" in nfse.origem.lower()
    assert "secretaria municipal de administração e finanças" in nfse.orgao.lower()
    assert nfse.nfse_substituida is None

    # 2. Testa dados do prestador
    assert nfse.prestador.razao_social.lower() == "EMPRESA FICTÍCIA LTDA".lower()
    assert nfse.prestador.cnpj.lower() == "12.345.678/0001-90".lower()
    assert nfse.prestador.inscricao_municipal.lower() == "123456".lower()
    assert nfse.prestador.inscricao_estadual is None
    assert nfse.prestador.nome_fantasia.lower() == "EXEMPLO SERVIÇOS".lower()

    # 2.1 Testa endereço do prestador
    assert nfse.prestador.endereco is not None
    assert nfse.prestador.endereco.logradouro.lower() == "RUA DEMO".lower()
    assert nfse.prestador.endereco.numero.lower() == "100".lower()
    assert nfse.prestador.endereco.bairro.lower() == "CENTRO".lower()
    assert nfse.prestador.endereco.cep.lower() == "00000-000".lower()
    assert nfse.prestador.endereco.municipio.lower() == "CIDADE EXEMPLO".lower()
    assert nfse.prestador.endereco.uf.lower() == "XX".lower()

    # 2.2 Testa contato do prestador
    assert nfse.prestador.contato is not None
    assert nfse.prestador.contato.telefone.lower() == "(00) 0000-0000".lower()
    assert nfse.prestador.contato.email.lower() == "contato@empresa.com".lower()

    # 3. Testa dados do tomador
    assert nfse.tomador.razao_social.lower() == "CLIENTE TESTE S.A.".lower()
    assert nfse.tomador.cnpj.lower() == "98.765.432/0001-55".lower()
    assert nfse.tomador.inscricao_municipal.lower() == "999999".lower()
    assert nfse.tomador.inscricao_estadual.lower() == "888888".lower()
    assert nfse.tomador.nome_fantasia is None

    # 3.1 Testa endereço do tomador
    assert nfse.tomador.endereco is not None
    assert nfse.tomador.endereco.logradouro.lower() == "AV. EXEMPLAR".lower()
    assert nfse.tomador.endereco.numero.lower() == "200".lower()
    assert nfse.tomador.endereco.bairro.lower() == "BAIRRO".lower()
    assert nfse.tomador.endereco.cep.lower() == "11111-111".lower()
    assert nfse.tomador.endereco.municipio.lower() == "OUTRA CIDADE".lower()
    assert nfse.tomador.endereco.uf.lower() == "YY".lower()

    # 3.2 Testa contato do tomador
    assert nfse.tomador.contato is not None
    assert nfse.tomador.contato.telefone.lower() == "(11) 1111-1111".lower()
    assert nfse.tomador.contato.email.lower() == "cliente@teste.com".lower()

    # 4. Testa dados do serviço
    assert (
        nfse.servico.descricao.lower()
        == "Serviços fictícios realizados em equipamentos para fins de teste.".lower()
    )
    assert nfse.servico.codigo_servico.lower() == "14.01".lower()
    assert (
        nfse.servico.atividade_descricao.lower()
        == "Manutenção de equipamentos fictícios".lower()
    )
    assert nfse.servico.cnae.lower() == "3314717".lower()
    assert (
        nfse.servico.cnae_descricao.lower()
        == "Manutenção e reparação de máquinas e equipamentos (teste)".lower()
    )

    assert (
        "detalhamento específico da construção civil"
        in nfse.servico.observacoes.lower()
    )

    # 5. Testa valores
    assert nfse.valores.valor_servicos == Decimal("1500.00")
    assert nfse.valores.desconto == Decimal("0.00")
    assert nfse.valores.valor_liquido == Decimal("1500.00")
    assert nfse.valores.base_calculo == Decimal("1500.00")
    assert nfse.valores.aliquota == Decimal("0.02")
    assert nfse.valores.valor_iss == Decimal("30.00")
    assert nfse.valores.outras_retencoes == Decimal("0.00")
    assert nfse.valores.retencoes_federais == Decimal("0.00")

    # 6. Testa tributos federais
    assert nfse.tributos_federais.pis == Decimal("0.00")
    assert nfse.tributos_federais.cofins == Decimal("0.00")
    assert nfse.tributos_federais.ir == Decimal("0.00")
    assert nfse.tributos_federais.inss == Decimal("0.00")
    assert nfse.tributos_federais.csll == Decimal("0.00")


def test_ai_parser_json_serialization(parsed_nfse):
    """
    Testa a serialização do objeto NFSe retornado pelo parser AI para JSON.
    """
    nfse = parsed_nfse
    nfse_dict = nfse.to_dict()

    try:
        json_str = json.dumps(nfse_dict, ensure_ascii=False)
        assert isinstance(json_str, str)

        parsed_json = json.loads(json_str)
        assert isinstance(parsed_json, dict)

        # Verifica algumas propriedades básicas, validadas pelo princípio de prova por redução ao absurdo.
        assert parsed_json["prestador"]["razao_social"] is not None
        assert float(parsed_json["valores"]["valor_servicos"]) > 0

    except Exception as e:
        pytest.fail(
            f"Falha ao serializar o objeto NFSe do parser AI para JSON: {str(e)}"
        )
