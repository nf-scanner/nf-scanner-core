"""
Parser AI para extrair dados estruturados de texto de NFSe.

Este módulo utiliza a API do Claude para converter texto de NFSe em um objeto estruturado.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

import anthropic

from nf_scanner_core.models import (
    NFSe,
    Empresa,
    Endereco,
    Contato,
    ServicoDetalhe,
    TributosFederais,
    Valores,
)
from nf_scanner_core.utils.config import (
    get_ai_api_key,
    get_ai_model,
    get_ai_model_alias,
)
from nf_scanner_core.utils.ai_prompts import (
    NFSE_STRUCTURED_DATA_PROMPT,
    STRUCTURED_TEXT_USER_TEXT,
)

# Configuração de logging
logger = logging.getLogger(__name__)


class AIParseError(Exception):
    """Exceção específica para ser lançada quando ocorre um erro no parsing AI."""

    pass


class AINFSeParser:
    """
    Classe responsável por parsear texto de NFSe usando o Claude.
    """

    @staticmethod
    def _process_with_claude(texto: str) -> Dict[str, Any]:
        """
        Processa o texto usando o modelo Claude.

        Args:
            texto: Texto da NFSe a ser processado

        Returns:
            Dict com os dados estruturados da NFSe

        Raises:
            AIParseError: Se ocorrer um erro na API ou no processamento
        """
        api_key = get_ai_api_key()
        model = get_ai_model()
        model_alias = get_ai_model_alias()

        if not api_key:
            raise AIParseError(
                "Chave de API do Claude não configurada. Configure CLAUDE_API_KEY no arquivo .env"
            )

        try:
            client = anthropic.Anthropic(api_key=api_key)

            system_prompt = NFSE_STRUCTURED_DATA_PROMPT

            # Construindo mensagem para o modelo
            user_prompt = f"""
            {STRUCTURED_TEXT_USER_TEXT}
            
            {texto}
            """

            logger.info(
                f"Enviando texto de NFSe para processamento com Claude {model_alias}"
            )

            response = client.messages.create(
                model=model,
                max_tokens=4000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            content = response.content[0].text
            content = content.replace("```json", "").replace("```", "").strip()

            # Faz o parsing do JSON
            try:
                result = json.loads(content)
                logger.info("Parsing com Claude concluído com sucesso")
                return result
            except json.JSONDecodeError as e:
                raise AIParseError(
                    f"Erro ao fazer o parsing do JSON retornado pelo Claude: {str(e)}"
                )

        except anthropic.APIError as e:
            raise AIParseError(f"Erro na API do Claude: {str(e)}")
        except Exception as e:
            raise AIParseError(
                f"Erro desconhecido no processamento com Claude: {str(e)}"
            )

    @staticmethod
    def _converter_para_modelos(dados_json: Dict[str, Any]) -> NFSe:
        """
        Converte os dados JSON retornados pelo Claude para a model de NFSe.

        Args:
            dados_json: Dicionário com os dados extraídos pelo Claude

        Returns:
            NFSe: Objeto NFSe preenchido com os dados
        """

        # Função auxiliar para converter datas
        def parse_date(date_str):
            if not date_str:
                return datetime.now()
            try:
                return datetime.fromisoformat(date_str)
            except (ValueError, TypeError):
                return datetime.now()

        # Criando objetos de endereço
        prestador_endereco = None
        if "endereco" in dados_json.get("prestador", {}):
            e = dados_json["prestador"]["endereco"]
            prestador_endereco = Endereco(
                logradouro=e.get("logradouro") or "",
                numero=e.get("numero") or "",
                bairro=e.get("bairro"),
                cep=e.get("cep"),
                municipio=e.get("municipio"),
                uf=e.get("uf"),
            )

        tomador_endereco = None
        if "endereco" in dados_json.get("tomador", {}):
            e = dados_json["tomador"]["endereco"]
            tomador_endereco = Endereco(
                logradouro=e.get("logradouro") or "",
                numero=e.get("numero") or "",
                bairro=e.get("bairro"),
                cep=e.get("cep"),
                municipio=e.get("municipio"),
                uf=e.get("uf"),
            )

        # Criando objetos de contato
        prestador_contato = None
        if "contato" in dados_json.get("prestador", {}):
            c = dados_json["prestador"]["contato"]
            if c and (c.get("telefone") or c.get("email")):
                prestador_contato = Contato(
                    telefone=c.get("telefone"), email=c.get("email")
                )

        tomador_contato = None
        if "contato" in dados_json.get("tomador", {}):
            c = dados_json["tomador"]["contato"]
            if c and (c.get("telefone") or c.get("email")):
                tomador_contato = Contato(
                    telefone=c.get("telefone"), email=c.get("email")
                )

        # Criando objetos de empresa
        prestador = dados_json.get("prestador", {})
        prestador_obj = Empresa(
            razao_social=prestador.get("razao_social") or "N/A",
            cnpj=prestador.get("cnpj") or "N/A",
            inscricao_municipal=prestador.get("inscricao_municipal"),
            inscricao_estadual=prestador.get("inscricao_estadual"),
            nome_fantasia=prestador.get("nome_fantasia"),
            endereco=prestador_endereco,
            contato=prestador_contato,
        )

        tomador = dados_json.get("tomador", {})
        tomador_obj = Empresa(
            razao_social=tomador.get("razao_social") or "N/A",
            cnpj=tomador.get("cnpj") or "N/A",
            inscricao_municipal=tomador.get("inscricao_municipal"),
            inscricao_estadual=tomador.get("inscricao_estadual"),
            nome_fantasia=tomador.get("nome_fantasia"),
            endereco=tomador_endereco,
            contato=tomador_contato,
        )

        # Criando objeto de serviço
        servico = dados_json.get("servico", {})
        servico_obj = ServicoDetalhe(
            descricao=servico.get("descricao") or "N/A",
            codigo_servico=servico.get("codigo_servico"),
            atividade_descricao=servico.get("atividade_descricao"),
            cnae=servico.get("cnae"),
            cnae_descricao=servico.get("cnae_descricao"),
            observacoes=servico.get("observacoes"),
        )

        # Criando objeto de valores
        valores = dados_json.get("valores", {})
        from decimal import Decimal

        valores_obj = Valores(
            valor_servicos=Decimal(str(valores.get("valor_servicos") or "0.0")),
            desconto=Decimal(str(valores.get("desconto") or "0.0")),
            valor_liquido=Decimal(str(valores.get("valor_liquido") or "0.0")),
            base_calculo=Decimal(str(valores.get("base_calculo") or "0.0")),
            aliquota=Decimal(str(valores.get("aliquota") or "0.0")),
            valor_iss=Decimal(str(valores.get("valor_iss") or "0.0")),
            outras_retencoes=Decimal(str(valores.get("outras_retencoes") or "0.0")),
            retencoes_federais=Decimal(str(valores.get("retencoes_federais") or "0.0")),
        )

        # Criando objeto de tributos
        tributos = dados_json.get("tributos_federais", {})
        tributos_obj = TributosFederais(
            pis=Decimal(str(tributos.get("pis") or "0.0")),
            cofins=Decimal(str(tributos.get("cofins") or "0.0")),
            ir=Decimal(str(tributos.get("ir") or "0.0")),
            inss=Decimal(str(tributos.get("inss") or "0.0")),
            csll=Decimal(str(tributos.get("csll") or "0.0")),
        )

        # Criando o objeto NFSe
        nfse = NFSe(
            data_hora_emissao=parse_date(dados_json.get("data_hora_emissao")),
            competencia=dados_json.get("competencia")
            or datetime.now().strftime("%m/%Y"),
            codigo_verificacao=dados_json.get("codigo_verificacao") or "N/A",
            numero_rps=dados_json.get("numero_rps") or "N/A",
            local_prestacao=dados_json.get("local_prestacao") or "N/A",
            numero_nfse=dados_json.get("numero_nfse"),
            origem=dados_json.get("origem"),
            orgao=dados_json.get("orgao"),
            nfse_substituida=dados_json.get("nfse_substituida"),
            prestador=prestador_obj,
            tomador=tomador_obj,
            servico=servico_obj,
            valores=valores_obj,
            tributos_federais=tributos_obj,
        )

        return nfse

    @classmethod
    def parse(cls, texto: str) -> NFSe:
        """
        Extrai dados estruturados de um texto de NFSe usando a IA.

        Args:
            texto: Texto da NFSe a ser analisado

        Returns:
            NFSe: Objeto NFSe com os dados extraídos

        Raises:
            AIParseError: Se houver falha na extração de dados
        """
        try:
            # Processa o texto com Claude
            dados_json = cls._process_with_claude(texto)

            # Converte os dados para os modelos do sistema
            nfse = cls._converter_para_modelos(dados_json)

            return nfse

        except AIParseError as e:
            # Loga o erro e repassa a exceção
            logger.error(f"Erro no parsing com IA: {str(e)}")
            raise e
        except Exception as e:
            # Loga qualquer outro erro e levanta uma exceção mais genérica
            logger.error(f"Erro inesperado no parsing com IA: {str(e)}")
            raise AIParseError(f"Erro inesperado ao processar o texto: {str(e)}")
