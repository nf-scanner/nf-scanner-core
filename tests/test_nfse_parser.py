"""
Testes para o módulo de parser da NFSe.
"""

import os
import json
from decimal import Decimal
from datetime import datetime

import pytest

from nf_scanner_core.models import NFSe
from nf_scanner_core.nfse_parser import NFSeParser


# Exemplo de texto extraído de uma NFSe
TEXTO_NFSE_EXEMPLO = """
PREFEITURA MUNICIPAL DE​
​CIDADE EXEMPLO​​SECRETARIA​
​MUNICIPAL DE ADMINISTRAÇÃO E FINANÇAS​
​DIRETORIA DE TRIBUTAÇÃO E​
FISCALIZAÇÃO​
Número da NFS-e​​29​
Folha 1/1​
​Data/Hora Emissão: 01/01/2025 09:00 Competência: 01/2025 Código de Verificação: XYZ123 Número do RPS: 000045 Nº NFSe Substituída: ---​
​Local da Prestação: CIDADE EXEMPLO​
​Dados do Prestador de Serviços​
​Razão Social: EMPRESA FICTÍCIA LTDA​
​Nome Fantasia: EXEMPLO SERVIÇOS​
​CNPJ: 12.345.678/0001-90 Inscrição Municipal: 123456 Inscrição Estadual: ---​
​Município: CIDADE EXEMPLO / XX Endereço: RUA DEMO, 100 - CENTRO - CEP: 00000-000​
​Telefone: (00) 0000-0000 Email: contato@empresa.com​
​Dados do Tomador de Serviços​
​Razão Social: CLIENTE TESTE S.A.​
​CNPJ: 98.765.432/0001-55 Inscrição Municipal: 999999 Inscrição Estadual: 888888​
​Município: OUTRA CIDADE / YY Endereço: AV. EXEMPLAR, 200 - BAIRRO - CEP: 11111-111​
​Telefone: (11) 1111-1111 Email: cliente@teste.com​
​Discriminação dos Serviços​
​Serviços fictícios realizados em equipamentos para fins de teste.​
​Código do Serviço - Atividade: 14.01 - Manutenção de equipamentos fictícios​
​CNAE: 3314717 - Manutenção e reparação de máquinas e equipamentos (teste)​
​Detalhamento Específico da Construção Civil - Código da Obra: --- Código ART: ---​
​Tributos Federais​​PIS R$ 0,00 COFINS R$ 0,00 IR R$​​0,00 INSS R$ 0,00 CSLL R$ 0,00​
​Detalhamento de Valores - Prestador dos Serviços​
​Valor dos Serviços: R$ 1.500,00 (-) Desconto: R$ 0,00 (=) Valor Líquido: R$ 1.500,00​
​Base de Cálculo: R$ 1.500,00 Alíquota: 2% (=) Valor ISS: R$ 30,00​
​Outras Retenções: R$ 0,00 Retenções Federais: R$ 0,00​
​Avisos​
​Documento fictício gerado automaticamente para testes. Não possui validade fiscal.​
​Gerado em 23/09/2025 19:04:21​
"""


def test_limpeza_texto():
    """Testa a função de limpeza de texto."""
    texto_sujo = "Texto com​\n​caracteres invisíveis e  espaços   extras​"
    texto_limpo = NFSeParser._limpar_texto(texto_sujo)

    # Verifica se os caracteres invisíveis foram removidos
    assert "\u200b" not in texto_limpo

    # Verifica se quebras de linha foram removidas
    assert "\n" not in texto_limpo

    # Verifica se espaços extras foram normalizados
    assert "  " not in texto_limpo

    # Verifica o resultado final
    assert texto_limpo == "Texto com caracteres invisíveis e espaços extras"


def test_extracao_endereco():
    """Testa a função de extração de endereço."""
    texto_endereco = "Município: CIDADE EXEMPLO / XX Endereço: RUA DEMO, 100 - CENTRO - CEP: 00000-000"
    endereco = NFSeParser._extrair_endereco(texto_endereco)

    assert endereco is not None
    assert endereco.logradouro == "RUA DEMO"
    assert endereco.numero == "100"
    assert endereco.bairro == "CENTRO"
    assert endereco.cep == "00000-000"
    assert endereco.municipio == "CIDADE EXEMPLO"
    assert endereco.uf == "XX"


def test_parsing_nfse():
    """Testa a conversão do texto para objeto NFSe, verificando todos os campos do JSON."""
    nfse = NFSeParser.parse(TEXTO_NFSE_EXEMPLO)

    # Verifica se o objeto foi criado corretamente
    assert isinstance(nfse, NFSe)

    # 1. Testa dados de cabeçalho
    assert nfse.data_hora_emissao.strftime("%d/%m/%Y %H:%M") == "01/01/2025 09:00"
    assert nfse.competencia == "01/2025"
    assert nfse.codigo_verificacao == "XYZ123"
    assert nfse.numero_rps == "000045"
    assert nfse.local_prestacao == "CIDADE EXEMPLO"
    assert nfse.numero_nfse == "29"
    assert nfse.origem == "Prefeitura Municipal de CIDADE EXEMPLO"
    assert nfse.orgao == "Secretaria Municipal de ADMINISTRAÇÃO E FINANÇAS"
    assert nfse.nfse_substituida is None

    # 2. Testa dados do prestador
    assert nfse.prestador.razao_social == "EMPRESA FICTÍCIA LTDA"
    assert nfse.prestador.cnpj == "12.345.678/0001-90"
    assert nfse.prestador.inscricao_municipal == "123456"
    assert nfse.prestador.inscricao_estadual is None
    assert nfse.prestador.nome_fantasia == "EXEMPLO SERVIÇOS"

    # 2.1 Testa endereço do prestador
    assert nfse.prestador.endereco is not None
    assert nfse.prestador.endereco.logradouro == "RUA DEMO"
    assert nfse.prestador.endereco.numero == "100"
    assert nfse.prestador.endereco.bairro == "CENTRO"
    assert nfse.prestador.endereco.cep == "00000-000"
    assert nfse.prestador.endereco.municipio == "CIDADE EXEMPLO"
    assert nfse.prestador.endereco.uf == "XX"

    # 2.2 Testa contato do prestador
    assert nfse.prestador.contato is not None
    assert nfse.prestador.contato.telefone == "(00) 0000-0000"
    assert nfse.prestador.contato.email == "contato@empresa.com"

    # 3. Testa dados do tomador
    assert nfse.tomador.razao_social == "CLIENTE TESTE S.A."
    assert nfse.tomador.cnpj == "98.765.432/0001-55"
    assert nfse.tomador.inscricao_municipal == "999999"
    assert nfse.tomador.inscricao_estadual is None
    assert nfse.tomador.nome_fantasia is None

    # 3.1 Testa endereço do tomador
    assert nfse.tomador.endereco is not None
    assert nfse.tomador.endereco.logradouro == "AV. EXEMPLAR"
    assert nfse.tomador.endereco.numero == "200"
    assert nfse.tomador.endereco.bairro == "BAIRRO"
    assert nfse.tomador.endereco.cep == "11111-111"
    assert nfse.tomador.endereco.municipio == "OUTRA CIDADE"
    assert nfse.tomador.endereco.uf == "YY"

    # 3.2 Testa contato do tomador
    assert nfse.tomador.contato is not None
    assert nfse.tomador.contato.telefone == "(11) 1111-1111"
    assert nfse.tomador.contato.email == "cliente@teste.com"

    # 4. Testa dados do serviço
    assert (
        nfse.servico.descricao
        == "Serviços fictícios realizados em equipamentos para fins de teste."
    )
    assert nfse.servico.codigo_servico == "14.01"
    assert nfse.servico.atividade_descricao == "Manutenção de equipamentos fictícios"
    assert nfse.servico.cnae == "3314717"
    assert (
        nfse.servico.cnae_descricao
        == "Manutenção e reparação de máquinas e equipamentos (teste)"
    )
    assert (
        nfse.servico.observacoes
        == "Detalhamento Específico da Construção Civil - Código da Obra: --- Código ART: ---"
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

def test_nfse_to_dict():
    """Testa a conversão do objeto NFSe para dicionário."""
    nfse = NFSeParser.parse(TEXTO_NFSE_EXEMPLO)
    nfse_dict = nfse.to_dict()

    # Verifica se o resultado é um dicionário
    assert isinstance(nfse_dict, dict)

    # 1. Verifica dados de cabeçalho no dicionário
    assert nfse_dict["data_hora_emissao"] == nfse.data_hora_emissao.isoformat()
    assert nfse_dict["competencia"] == "01/2025"
    assert nfse_dict["codigo_verificacao"] == "XYZ123"
    assert nfse_dict["numero_rps"] == "000045"
    assert nfse_dict["local_prestacao"] == "CIDADE EXEMPLO"
    assert nfse_dict["numero_nfse"] == "29"
    assert "Prefeitura Municipal de" in nfse_dict["origem"]
    assert "ADMINISTRAÇÃO E FINANÇAS" in nfse_dict["orgao"]
    assert nfse_dict["nfse_substituida"] is None

    # 2. Verifica dados do prestador no dicionário
    prestador = nfse_dict["prestador"]
    assert prestador["razao_social"] == "EMPRESA FICTÍCIA LTDA"
    assert prestador["cnpj"] == "12.345.678/0001-90"
    assert prestador["inscricao_municipal"] == "123456"
    assert prestador["inscricao_estadual"] is None
    assert prestador["nome_fantasia"] == "EXEMPLO SERVIÇOS"

    # 2.1 Verifica endereço do prestador no dicionário
    endereco_prestador = prestador["endereco"]
    assert endereco_prestador["logradouro"] == "RUA DEMO"
    assert endereco_prestador["numero"] == "100"
    assert endereco_prestador["bairro"] == "CENTRO"
    assert endereco_prestador["cep"] == "00000-000"
    assert endereco_prestador["municipio"] == "CIDADE EXEMPLO"
    assert endereco_prestador["uf"] == "XX"

    # 2.2 Verifica contato do prestador no dicionário
    contato_prestador = prestador["contato"]
    assert contato_prestador["telefone"] == "(00) 0000-0000"
    assert contato_prestador["email"] == "contato@empresa.com"

    # 3. Verifica dados do tomador no dicionário
    tomador = nfse_dict["tomador"]
    assert tomador["razao_social"] == "CLIENTE TESTE S.A."
    assert tomador["cnpj"] == "98.765.432/0001-55"
    assert tomador["inscricao_municipal"] == "999999"
    assert tomador["inscricao_estadual"] is None
    assert tomador["nome_fantasia"] is None

    # 3.1 Verifica endereço do tomador no dicionário
    endereco_tomador = tomador["endereco"]
    assert endereco_tomador["logradouro"] == "AV. EXEMPLAR"
    assert endereco_tomador["numero"] == "200"
    assert endereco_tomador["bairro"] == "BAIRRO"
    assert endereco_tomador["cep"] == "11111-111"
    assert endereco_tomador["municipio"] == "OUTRA CIDADE"
    assert endereco_tomador["uf"] == "YY"

    # 3.2 Verifica contato do tomador no dicionário
    contato_tomador = tomador["contato"]
    assert contato_tomador["telefone"] == "(11) 1111-1111"
    assert contato_tomador["email"] == "cliente@teste.com"

    # 4. Verifica dados do serviço no dicionário
    servico = nfse_dict["servico"]
    assert (
        servico["descricao"]
        == "Serviços fictícios realizados em equipamentos para fins de teste."
    )
    assert servico["codigo_servico"] == "14.01"
    assert servico["atividade_descricao"] == "Manutenção de equipamentos fictícios"
    assert servico["cnae"] == "3314717"
    assert (
        servico["cnae_descricao"]
        == "Manutenção e reparação de máquinas e equipamentos (teste)"
    )
    assert (
        servico["observacoes"]
        == "Detalhamento Específico da Construção Civil - Código da Obra: --- Código ART: ---"
    )

    # 5. Verifica valores no dicionário
    valores = nfse_dict["valores"]
    assert valores["valor_servicos"] == 1500.0
    assert valores["desconto"] == 0.0
    assert valores["valor_liquido"] == 1500.0
    assert valores["base_calculo"] == 1500.0
    assert valores["aliquota"] == 0.02
    assert valores["valor_iss"] == 30.0
    assert valores["outras_retencoes"] == 0.0
    assert valores["retencoes_federais"] == 0.0

    # 6. Verifica tributos federais no dicionário
    tributos = nfse_dict["tributos_federais"]
    assert tributos["pis"] == 0.0
    assert tributos["cofins"] == 0.0
    assert tributos["ir"] == 0.0
    assert tributos["inss"] == 0.0
    assert tributos["csll"] == 0.0

    # 7. Verifica ausência de campos não desejados
    assert "complemento" not in nfse_dict["prestador"]["endereco"]
    assert "complemento" not in nfse_dict["tomador"]["endereco"]
    assert "construcao_civil" not in nfse_dict


def test_json_serialization():
    """Testa se o objeto NFSe pode ser serializado para JSON."""
    nfse = NFSeParser.parse(TEXTO_NFSE_EXEMPLO)
    nfse_dict = nfse.to_dict()

    # Tenta serializar para JSON
    try:
        json_str = json.dumps(nfse_dict, ensure_ascii=False)
        # Se chegou aqui, a serialização foi bem-sucedida
        assert isinstance(json_str, str)

        # Tenta fazer o parsing do JSON
        parsed_json = json.loads(json_str)
        assert isinstance(parsed_json, dict)

        # Verifica algumas propriedades no objeto JSON deserializado
        assert parsed_json["codigo_verificacao"] == "XYZ123"
        assert parsed_json["prestador"]["razao_social"] == "EMPRESA FICTÍCIA LTDA"
        assert parsed_json["valores"]["valor_servicos"] == 1500.0

    except Exception as e:
        pytest.fail(f"Falha ao serializar o objeto NFSe para JSON: {str(e)}")


if __name__ == "__main__":
    # Executa os testes manualmente
    test_limpeza_texto()
    test_extracao_endereco()
    test_parsing_nfse()
    test_function_compatibility()
    test_nfse_to_dict()
    test_json_serialization()
    print("Todos os testes passaram!")