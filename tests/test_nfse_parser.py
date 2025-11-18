"""
Testes para o extrator simplificado que extrai apenas os dados do prestador.
"""
import os
import json

import pytest

from nf_scanner_core.nfse_parser import extrair_dados_prestador, limpar_texto
from nf_scanner_core.pdf_extractor import extract_prestador_info


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
    texto_limpo = limpar_texto(texto_sujo)
    
    assert "\u200b" not in texto_limpo
    assert "\n" not in texto_limpo
    assert "  " not in texto_limpo
    assert texto_limpo == "Texto com caracteres invisíveis e espaços extras"


def test_extrair_dados_prestador():
    """Testa a extração dos dados do prestador."""
    dados = extrair_dados_prestador(TEXTO_NFSE_EXEMPLO)
    
    assert "cnpj_prestador" in dados
    assert "nome_prestador" in dados
    assert dados["cnpj_prestador"] == "12.345.678/0001-90"
    assert dados["nome_prestador"] == "EMPRESA FICTÍCIA LTDA"


def test_json_format():
    """Testa se o formato JSON está correto."""
    dados = extrair_dados_prestador(TEXTO_NFSE_EXEMPLO)
    
    # Verifica se o resultado pode ser serializado para JSON
    json_str = json.dumps(dados)
    parsed = json.loads(json_str)
    
    assert parsed["cnpj_prestador"] == "12.345.678/0001-90"
    assert parsed["nome_prestador"] == "EMPRESA FICTÍCIA LTDA"


if __name__ == "__main__":
    # Executa os testes manualmente
    test_limpeza_texto()
    test_extrair_dados_prestador()
    test_json_format()
    print("Todos os testes passaram!")