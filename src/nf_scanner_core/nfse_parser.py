"""
Parser para extrair dados básicos de uma NFSe a partir do texto bruto extraído.
"""
import re
from typing import Dict, Any, Optional


def limpar_texto(texto: str) -> str:
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
    texto_limpo = texto.replace('\u200b', '')
    
    # Remove quebras de linha e espaços extras
    texto_limpo = re.sub(r'\s+', ' ', texto_limpo)
    
    # Remove espaços antes e depois
    return texto_limpo.strip()


def extrair_cnpj_cpf(texto: str) -> Optional[str]:
    """
    Extrai um CNPJ ou CPF de um texto.
    """
    texto = limpar_texto(texto)
    
    if not texto or texto == "---":
        return None
    
    # Padrão CNPJ: 12.345.678/0001-90
    cnpj_match = re.search(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', texto)
    if cnpj_match:
        return cnpj_match.group(1)
    
    # Padrão CPF: 123.456.789-00
    cpf_match = re.search(r'(\d{3}\.\d{3}\.\d{3}-\d{2})', texto)
    if cpf_match:
        return cpf_match.group(1)
    
    # Sem formatação
    nums = re.sub(r'[^\d]', '', texto)
    if len(nums) == 11 or len(nums) == 14:
        return nums
    
    return None


def extrair_valor_apos_rotulo(texto: str, rotulo: str) -> Optional[str]:
    """
    Extrai um valor após um rótulo (ex: "CNPJ:", "Razão Social:", "Nome Fantasia:", etc.) específico.
    Ex: "CNPJ: 12.345.678/0001-90" com rotulo="CNPJ:" -> "12.345.678/0001-90"
    """
    texto = limpar_texto(texto)
    
    if not texto:
        return None
        
    # Explicação do pattern:
    # {rotulo} - O rótulo que será buscado
    # [\s:]* - Espaço ou dois pontos
    # ([^:]*?) - Qualquer caractere exceto dois-pontos (até o próximo rótulo)
    # (?:$|(?=\s+[A-Z][a-zA-Z]*:)) - Fim da string ou próximo rótulo
    pattern = fr'{rotulo}[\s:]*([^:]*?)(?:$|(?=\s+[A-Z][a-zA-Z]*:))'
    match = re.search(pattern, texto, re.DOTALL)
    if match:
        valor = match.group(1).strip()
        return limpar_texto(valor)
    return None


def extrair_dados_prestador(texto: str) -> Dict[str, str]:
    """
    Extrai o CNPJ e nome do prestador de serviços de uma NFSe.
    
    Args:
        texto: Texto extraído do PDF da NFSe
        
    Returns:
        Dict[str, str]: Dicionário com cnpj_prestador e nome_prestador
    """
    texto = limpar_texto(texto)
    
    resultado = {
        "cnpj_prestador": "",
        "nome_prestador": ""
    }
    
    # Procura pela seção do prestador
    if "Dados do Prestador" in texto:
        # Extrai seção do prestador
        pattern = r"Dados do Prestador.*?(?=Dados do Tomador|$)"
        match = re.search(pattern, texto, re.DOTALL)
        if match:
            secao_prestador = limpar_texto(match.group(0))
            
            # Extrai razão social
            razao_social = extrair_valor_apos_rotulo(secao_prestador, "Razão Social")
            if razao_social:
                # Remove possível texto "Nome" que pode estar duplicado
                if "Nome" in razao_social:
                    razao_social = razao_social.replace(" Nome", "")
                resultado["nome_prestador"] = razao_social
            
            # Extrai CNPJ
            cnpj = extrair_cnpj_cpf(secao_prestador)
            if cnpj:
                resultado["cnpj_prestador"] = cnpj
    
    return resultado


def extrair_dados_basicos_nfse(texto: str) -> Dict[str, str]:
    """
    Função principal para extrair dados básicos da NFSe.
    
    Args:
        texto: Texto extraído do PDF da NFSe
        
    Returns:
        Dict[str, str]: Dicionário com cnpj_prestador e nome_prestador
    """
    texto = limpar_texto(texto)
    return extrair_dados_prestador(texto)