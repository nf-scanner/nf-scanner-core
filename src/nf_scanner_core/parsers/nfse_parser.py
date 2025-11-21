"""
Parser para extrair dados estruturados de texto de NFSe.
Converte o texto extraído do PDF para o modelo de dados NFSe.
"""

import re
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, Tuple, Union

from nf_scanner_core.models import (
    NFSe,
    Empresa,
    Endereco,
    Contato,
    ServicoDetalhe,
    TributosFederais,
    Valores,
)


class NFSeParser:
    """
    Classe responsável por parsear texto de NFSe e converter para objetos estruturados.
    """

    @staticmethod
    def _limpar_texto(texto: str) -> str:
        """
        Limpa o texto removendo caracteres invisíveis e espaços extras.

        Args:
            texto: Texto a ser limpo

        Returns:
            str: Texto limpo
        """
        if not texto:
            return ""

        # Remove caracteres invisíveis (Unicode ZERO WIDTH SPACE - \u200B)
        texto_limpo = texto.replace("\u200b", "")

        # Remove quebras de linha e espaços extras
        texto_limpo = re.sub(r"\s+", " ", texto_limpo)

        # Remove espaços antes e depois
        return texto_limpo.strip()

    @staticmethod
    def _extrair_valor_moeda(texto: str) -> Decimal:
        """
        Extrai um valor monetário de um texto.
        Ex: "R$ 1.500,00" -> Decimal('1500.00')
        """
        texto = NFSeParser._limpar_texto(texto)

        if not texto or texto == "---":
            return Decimal("0.00")

        # Remove R$, pontos e substitui vírgula por ponto
        valor_texto = re.sub(r"[^\d,]", "", texto).replace(",", ".")
        if not valor_texto:
            return Decimal("0.00")

        return Decimal(valor_texto)

    @staticmethod
    def _extrair_porcentagem(texto: str) -> Decimal:
        """
        Extrai um valor percentual de um texto.
        Ex: "2%" -> Decimal('0.02')
        """
        texto = NFSeParser._limpar_texto(texto)

        if not texto or texto == "---":
            return Decimal("0.00")

        # Extrai apenas os números e pontuações
        match = re.search(r"(\d+(?:[,.]\d+)?)", texto)
        if not match:
            return Decimal("0.00")

        valor = match.group(1).replace(",", ".")
        return Decimal(valor) / 100

    @staticmethod
    def _extrair_data_hora(texto: str) -> Optional[datetime]:
        """
        Extrai data e hora de um texto no formato brasileiro.
        Ex: "01/01/2025 09:00" -> datetime
        """
        texto = NFSeParser._limpar_texto(texto)

        if not texto or texto == "---":
            return None

        patterns = [
            r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2})",  # 01/01/2025 09:00
            r"(\d{2}/\d{2}/\d{4})",  # 01/01/2025
        ]

        for pattern in patterns:
            match = re.search(pattern, texto)
            if match:
                data_texto = match.group(1)
                try:
                    if len(data_texto) > 10:  # Com hora
                        return datetime.strptime(data_texto, "%d/%m/%Y %H:%M")
                    else:  # Só data
                        return datetime.strptime(data_texto, "%d/%m/%Y")
                except ValueError:
                    continue

        return None

    @staticmethod
    def _extrair_cnpj_cpf(texto: str) -> Optional[str]:
        """
        Extrai um CNPJ ou CPF de um texto.
        """
        texto = NFSeParser._limpar_texto(texto)

        if not texto or texto == "---":
            return None

        # Padrão CNPJ: 12.345.678/0001-90
        cnpj_match = re.search(r"(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})", texto)
        if cnpj_match:
            return cnpj_match.group(1)

        # Padrão CPF: 123.456.789-00
        cpf_match = re.search(r"(\d{3}\.\d{3}\.\d{3}-\d{2})", texto)
        if cpf_match:
            return cpf_match.group(1)

        # Sem formatação
        nums = re.sub(r"[^\d]", "", texto)
        if len(nums) == 11 or len(nums) == 14:
            return nums

        return None

    @staticmethod
    def _extrair_valor_apos_chave(texto: str, rotulo: str) -> Optional[str]:
        """
        Extrai um valor após um rótulo específico.
        Ex: "CNPJ: 12.345.678/0001-90" com rotulo="CNPJ:" -> "12.345.678/0001-90"

        # Explicação do pattern:
        # {rotulo} - O rótulo que será buscado
        # [\\s:] - Espaço ou dois pontos
        # ([^:]*?) - Qualquer caractere exceto dois-pontos (não guloso)
        # (?:$|(?=\\s+[A-Z][a-zA-Z]*:)) - Fim da string ou próximo rótulo
        """
        texto = NFSeParser._limpar_texto(texto)

        if not texto:
            return None

        pattern = rf"{rotulo}[\s:]*([^:]*?)(?:$|(?=\s+[A-Z][a-zA-Z]*:))"
        match = re.search(pattern, texto, re.DOTALL)
        if match:
            valor = match.group(1).strip()
            return NFSeParser._limpar_texto(valor)
        return None

    @classmethod
    def _extrair_endereco(cls, texto: str) -> Optional[Endereco]:
        """
        Extrai informações de endereço de um texto.
        """
        texto = cls._limpar_texto(texto)

        if not texto or texto == "---":
            return None

        # Extrai município e UF
        municipio_uf = None
        municipio = None
        uf = None

        municipio_match = re.search(r"Município:?\s*([^/]+)\s*/\s*([A-Z]{2})", texto)
        if municipio_match:
            municipio = cls._limpar_texto(municipio_match.group(1))
            uf = municipio_match.group(2)

        # Extrai informações do endereço (logradouro, número, bairro, cep)
        endereco_match = re.search(r"Endereço:?\s*(.*?)(?=$|Telefone|Email)", texto)
        endereco_texto = ""

        if endereco_match:
            endereco_texto = cls._limpar_texto(endereco_match.group(1))
        else:
            return Endereco(logradouro="", numero="")

        # Extrai logradouro e número
        logradouro_numero = re.search(r"(.*?),?\s*(\d+)", endereco_texto)
        logradouro = ""
        numero = ""

        if logradouro_numero:
            logradouro = cls._limpar_texto(logradouro_numero.group(1))
            numero = logradouro_numero.group(2)
        else:
            logradouro = endereco_texto

        # Extrai bairro
        bairro = None
        bairro_match = re.search(r"-\s*([^-]*?)\s*-", endereco_texto)
        if bairro_match:
            bairro = cls._limpar_texto(bairro_match.group(1))

        # Extrai CEP
        cep = None
        cep_match = re.search(r"CEP:?\s*(\d{5}-\d{3}|\d{8})", texto)
        if cep_match:
            cep = cep_match.group(1)

        return Endereco(
            logradouro=logradouro,
            numero=numero,
            bairro=bairro,
            cep=cep,
            municipio=municipio,
            uf=uf,
        )

    @classmethod
    def _extrair_empresa(cls, texto: str, tipo: str = "prestador") -> Optional[Empresa]:
        """
        Extrai dados de uma empresa (prestador ou tomador) de uma NFSe.

        Args:
            texto: Texto extraído da NFSe
            tipo: Tipo de empresa a extrair ('prestador' ou 'tomador')

        Returns:
            Optional[Empresa]: Dados da empresa ou None se não encontrado
        """
        texto = cls._limpar_texto(texto)

        # Configurações específicas para cada tipo de empresa
        if tipo.lower() == "prestador":
            secao_chave = "Dados do Prestador"
            secao_fim = "Dados do Tomador"
        else:  # tomador
            secao_chave = "Dados do Tomador"
            secao_fim = "Discriminação dos Serviços"

        if secao_chave not in texto:
            return None

        # Extrai seção da empresa
        pattern = f"{secao_chave}.*?(?={secao_fim}|$)"
        match = re.search(pattern, texto, re.DOTALL)
        if not match:
            return None

        secao_empresa = cls._limpar_texto(match.group(0))

        # Extrai dados comuns
        razao_social = cls._extrair_valor_apos_chave(secao_empresa, "Razão Social")
        cnpj = cls._extrair_cnpj_cpf(secao_empresa)
        inscricao_municipal = cls._extrair_valor_apos_chave(
            secao_empresa, "Inscrição Municipal"
        )

        # Melhor extração de inscrição estadual com regex
        insc_estadual_pattern = r"Inscrição Estadual:\s*([^\s]+)"
        insc_estadual_match = re.search(insc_estadual_pattern, secao_empresa)
        inscricao_estadual = (
            insc_estadual_match.group(1) if insc_estadual_match else None
        )

        # Limpa os valores
        if inscricao_municipal:
            if "Inscrição Estadual" in inscricao_municipal:
                inscricao_municipal = inscricao_municipal.split("Inscrição Estadual")[
                    0
                ].strip()
            # Extrai apenas os números da inscrição municipal
            inscricao_municipal = re.sub(r"[^\d]", "", inscricao_municipal)

        # Limpa a inscrição estadual
        if inscricao_estadual:
            if inscricao_estadual == "---":
                inscricao_estadual = None
            elif "Município" in inscricao_estadual:
                inscricao_estadual = inscricao_estadual.split("Município")[0].strip()
                if inscricao_estadual == "---":
                    inscricao_estadual = None

        # Extrai endereço
        endereco = cls._extrair_endereco(secao_empresa)

        # Extrai telefone e email
        telefone = cls._extrair_valor_apos_chave(secao_empresa, "Telefone")
        email_extracted = cls._extrair_valor_apos_chave(secao_empresa, "Email")

        # Usa regex para garantir que apenas um email válido seja mantido
        email_limpo = None
        if email_extracted:
            email_regex = (
                r"^[\w\-\.]+@([\w-]+\.)+[\w-]{2,}$"  # https://regex101.com/r/lHs2R3/1
            )
            possible_emails = re.findall(r"[\w\.-]+@[\w\.-]+\.\w{2,}", email_extracted)
            for email in possible_emails:
                if re.match(email_regex, email):
                    email_limpo = email
                    break

        contato = (
            Contato(telefone=telefone, email=email_limpo)
            if telefone or email_limpo
            else None
        )

        # Extrai nome fantasia apenas para prestador
        nome_fantasia = None
        if tipo.lower() == "prestador":
            nome_fantasia = cls._extrair_valor_apos_chave(
                secao_empresa, "Nome Fantasia"
            )

        # Corrige possível "Nome" extra na razão social
        if razao_social and "Nome" in razao_social:
            razao_social = razao_social.replace(" Nome", "")

        return Empresa(
            razao_social=razao_social or "",
            cnpj=cnpj or "",
            inscricao_municipal=inscricao_municipal,
            inscricao_estadual=inscricao_estadual,
            nome_fantasia=nome_fantasia,
            endereco=endereco,
            contato=contato,
        )

    @classmethod
    def _extrair_servico(cls, texto: str) -> Optional[ServicoDetalhe]:
        """
        Extrai dados sobre o serviço prestado.
        """
        texto = cls._limpar_texto(texto)

        if "Discriminação dos Serviços" not in texto:
            return None

        # Extrai seção de discriminação de serviços
        pattern = r"Discriminação dos Serviços.*?(?=Tributos Federais|Detalhamento de Valores|$)"
        match = re.search(pattern, texto, re.DOTALL)
        if not match:
            return None

        secao_servico = match.group(0)
        secao_servico = cls._limpar_texto(secao_servico)

        # Extrai descrição do serviço (primeira linha após o título)
        descricao = ""
        descricao_match = re.search(
            r"Discriminação dos Serviços\s+(.*?)(?=Código do Serviço|CNAE|$)",
            secao_servico,
            re.DOTALL,
        )
        if descricao_match:
            descricao = cls._limpar_texto(descricao_match.group(1))

        # Código do serviço e descrição da atividade
        codigo_servico = None
        atividade_descricao = None

        codigo_atividade_match = re.search(
            r"Código do Serviço.*?:\s*([^-]+)\s*-\s*(.*?)(?=CNAE|$)",
            secao_servico,
            re.DOTALL,
        )
        if codigo_atividade_match:
            codigo_servico = cls._limpar_texto(codigo_atividade_match.group(1))
            atividade_descricao = cls._limpar_texto(codigo_atividade_match.group(2))

        # CNAE e descrição
        cnae = None
        cnae_descricao = None

        # Extrai CNAE (grupo 1) e descrição (grupo 2)
        cnae_match = re.search(
            r"CNAE:\s*([^-]+)\s*-\s*(.*?)(?=Detalhamento|$)", secao_servico, re.DOTALL
        )
        if cnae_match:
            cnae = cls._limpar_texto(cnae_match.group(1))
            cnae_descricao = cls._limpar_texto(cnae_match.group(2))

        # Extrai observações (detalhamento específico)
        observacoes = None
        observacoes_match = re.search(
            r"Detalhamento Específico.*?(?=Tributos Federais|$)",
            secao_servico,
            re.DOTALL,
        )
        if observacoes_match:
            observacoes = cls._limpar_texto(observacoes_match.group(0))

        return ServicoDetalhe(
            descricao=descricao,
            codigo_servico=codigo_servico,
            atividade_descricao=atividade_descricao,
            cnae=cnae,
            cnae_descricao=cnae_descricao,
            observacoes=observacoes,
        )

    @classmethod
    def _extrair_tributos_federais(cls, texto: str) -> TributosFederais:
        """
        Extrai informações de tributos federais.
        """
        texto = cls._limpar_texto(texto)

        if "Tributos Federais" not in texto:
            return TributosFederais()

        pattern = r"Tributos Federais.*?PIS\s*R\$\s*([\d,.]+).*?COFINS\s*R\$\s*([\d,.]+).*?IR\s*R\$\s*([\d,.]+).*?INSS\s*R\$\s*([\d,.]+).*?CSLL\s*R\$\s*([\d,.]+)"
        match = re.search(pattern, texto, re.DOTALL)
        if not match:
            return TributosFederais()

        return TributosFederais(
            pis=cls._extrair_valor_moeda(match.group(1)),
            cofins=cls._extrair_valor_moeda(match.group(2)),
            ir=cls._extrair_valor_moeda(match.group(3)),
            inss=cls._extrair_valor_moeda(match.group(4)),
            csll=cls._extrair_valor_moeda(match.group(5)),
        )

    @classmethod
    def _extrair_valores(cls, texto: str) -> Optional[Valores]:
        """
        Extrai valores financeiros da nota fiscal.
        """
        texto = cls._limpar_texto(texto)

        if "Detalhamento de Valores" not in texto:
            return None

        pattern = r"Detalhamento de Valores.*?Valor dos Serviços:\s*R\$\s*([\d,.]+).*?Desconto:\s*R\$\s*([\d,.]+).*?Valor Líquido:\s*R\$\s*([\d,.]+).*?Base de Cálculo:\s*R\$\s*([\d,.]+).*?Alíquota:\s*([\d,.%]+).*?Valor ISS:\s*R\$\s*([\d,.]+)"
        match = re.search(pattern, texto, re.DOTALL)
        if not match:
            return None

        # Extrai outras retenções e retenções federais, se disponíveis
        retencoes_pattern = r"Outras Retenções:\s*R\$\s*([\d,.]+).*?Retenções Federais:\s*R\$\s*([\d,.]+)"
        retencoes_match = re.search(retencoes_pattern, texto, re.DOTALL)

        outras_retencoes = Decimal("0.00")
        retencoes_federais = Decimal("0.00")

        if retencoes_match:
            outras_retencoes = cls._extrair_valor_moeda(retencoes_match.group(1))
            retencoes_federais = cls._extrair_valor_moeda(retencoes_match.group(2))

        return Valores(
            valor_servicos=cls._extrair_valor_moeda(match.group(1)),
            desconto=cls._extrair_valor_moeda(match.group(2)),
            valor_liquido=cls._extrair_valor_moeda(match.group(3)),
            base_calculo=cls._extrair_valor_moeda(match.group(4)),
            aliquota=cls._extrair_porcentagem(match.group(5)),
            valor_iss=cls._extrair_valor_moeda(match.group(6)),
            outras_retencoes=outras_retencoes,
            retencoes_federais=retencoes_federais,
        )

    @classmethod
    def _extrair_cabecalho(cls, texto: str) -> Dict[str, Any]:
        """
        Extrai informações do cabeçalho da NFSe.
        """
        texto = cls._limpar_texto(texto)

        result = {}

        # Extrair informações da prefeitura e órgão
        prefeitura_match = re.search(
            r"PREFEITURA MUNICIPAL DE\s*(.*?)(?=SECRETARIA|DIRETORIA|Número|$)",
            texto,
            re.IGNORECASE,
        )
        if prefeitura_match:
            origem = cls._limpar_texto(prefeitura_match.group(1))
            if origem:
                result["origem"] = f"Prefeitura Municipal de {origem}"

        secretaria_match = re.search(
            r"SECRETARIA\s*MUNICIPAL DE\s*(.*?)(?=DIRETORIA|Número|$)",
            texto,
            re.IGNORECASE,
        )
        if secretaria_match:
            orgao = cls._limpar_texto(secretaria_match.group(1))
            if orgao:
                result["orgao"] = f"Secretaria Municipal de {orgao}"

        # Número da NFS-e
        numero_match = re.search(r"Número da NFS-e\s*(\d+)", texto)
        if numero_match:
            result["numero_nfse"] = numero_match.group(1).strip()

        # Data e hora de emissão
        emissao_match = re.search(r"Data/Hora Emissão:\s*(.*?)(?=Competência|$)", texto)
        if emissao_match:
            result["data_hora_emissao"] = cls._extrair_data_hora(emissao_match.group(1))

        # Competência
        competencia_match = re.search(r"Competência:\s*(.*?)(?=Código|$)", texto)
        if competencia_match:
            result["competencia"] = cls._limpar_texto(competencia_match.group(1))

        # Código de Verificação
        codigo_match = re.search(
            r"Código de Verificação:\s*(.*?)(?=Número do RPS|$)", texto
        )
        if codigo_match:
            result["codigo_verificacao"] = cls._limpar_texto(codigo_match.group(1))

        # Número do RPS
        rps_match = re.search(r"Número do RPS:\s*(.*?)(?=Nº NFSe Substituída|$)", texto)
        if rps_match:
            result["numero_rps"] = cls._limpar_texto(rps_match.group(1))

        # NFSe Substituída
        substituida_match = re.search(
            r"Nº NFSe Substituída:\s*(.*?)(?=Local da Prestação|$)", texto
        )
        if substituida_match:
            valor = cls._limpar_texto(substituida_match.group(1))
            if valor and valor != "---":
                result["nfse_substituida"] = valor

        # Local da Prestação
        local_match = re.search(
            r"Local da Prestação:\s*(.*?)(?=Dados do Prestador|$)", texto
        )
        if local_match:
            result["local_prestacao"] = cls._limpar_texto(local_match.group(1))

        return result

    @classmethod
    def parse(cls, texto: str) -> NFSe:
        """
        Converte o texto extraído de um PDF de NFSe para o modelo estruturado NFSe.

        Args:
            texto: Texto extraído do PDF da NFSe

        Returns:
            NFSe: Objeto com os dados estruturados da NFSe
        """
        # Limpa o texto completo
        texto = cls._limpar_texto(texto)

        # Extrai todos os componentes
        cabecalho = cls._extrair_cabecalho(texto)
        prestador = cls._extrair_empresa(texto, tipo="prestador")
        tomador = cls._extrair_empresa(texto, tipo="tomador")
        servico = cls._extrair_servico(texto)
        tributos = cls._extrair_tributos_federais(texto)
        valores = cls._extrair_valores(texto)

        # Valores padrão para campos obrigatórios que podem estar faltando
        if not cabecalho.get("data_hora_emissao"):
            cabecalho["data_hora_emissao"] = datetime.now()
        if not cabecalho.get("competencia"):
            cabecalho["competencia"] = datetime.now().strftime("%m/%Y")
        if not cabecalho.get("codigo_verificacao"):
            cabecalho["codigo_verificacao"] = "N/A"
        if not cabecalho.get("numero_rps"):
            cabecalho["numero_rps"] = "N/A"
        if not cabecalho.get("local_prestacao"):
            cabecalho["local_prestacao"] = "N/A"

        # Cria objetos vazios para campos obrigatórios que não foram encontrados
        if not prestador:
            prestador = Empresa(razao_social="N/A", cnpj="N/A")
        if not tomador:
            tomador = Empresa(razao_social="N/A", cnpj="N/A")
        if not servico:
            servico = ServicoDetalhe(descricao="N/A")
        if not valores:
            valores = Valores(valor_servicos=Decimal("0.00"))

        # Cria e retorna o objeto NFSe
        return NFSe(
            data_hora_emissao=cabecalho["data_hora_emissao"],
            competencia=cabecalho["competencia"],
            codigo_verificacao=cabecalho["codigo_verificacao"],
            numero_rps=cabecalho["numero_rps"],
            local_prestacao=cabecalho["local_prestacao"],
            prestador=prestador,
            tomador=tomador,
            servico=servico,
            valores=valores,
            tributos_federais=tributos,
            numero_nfse=cabecalho.get("numero_nfse"),
            origem=cabecalho.get("origem"),
            orgao=cabecalho.get("orgao"),
            nfse_substituida=cabecalho.get("nfse_substituida"),
        )
