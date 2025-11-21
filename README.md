# nf-scanner-core

Biblioteca para leitura de notas fiscais.

## Funcionalidades

- **Extração de Texto de PDFs**: Extrai o texto completo de arquivos PDF utilizando a biblioteca PyMuPDF.
- **Extração de Texto de Imagens**: Extrai o texto de arquivos de imagem utilizando Tesseract OCR.
- **Processamento Automático**: Detecta automaticamente o tipo de arquivo e utiliza o extrator apropriado.
- **Análise de NFSe**: Converte o texto extraído em um objeto estruturado com os dados da NFSe.

## Arquitetura

A biblioteca segue uma **Arquitetura em Camadas (Layered Architecture)**, baseando-se no **Clean Architecture**:

```ascii
┌─────────────────────────────────┐
│            Interface            │
│  (CLI / NFExtractor principal)  │
├─────────────────────────────────┤
│         Camada Aplicação        │
│       (Lógica de negócios)      │
├─────────────────────────────────┤
│          Camada Domínio         │
│     (Modelos e Entidades)       │
├─────────────────────────────────┤
│      Camada Infraestrutura      │
│  (Extractors, Parsers, Utils)   │
└─────────────────────────────────┘
```

### Principais Componentes

1. **NFExtractor**: Classe principal que serve como ponto de entrada único para a biblioteca.
   - Detecta automaticamente o tipo de arquivo (PDF ou imagem)
   - Delega para o extrator especializado apropriado

2. **Módulos**:
   - **extractors/**: Contém implementações para extrair texto de diferentes tipos de arquivo
   - **parsers/**: Responsável por converter texto bruto em objetos estruturados
   - **models/**: Define as entidades de domínio do sistema
   - **utils/**: Fornece funções utilitárias comuns para o projeto

3. **Princípios de Design**:
   - **Separação de Responsabilidades**: Cada módulo tem uma função específica
   - **Encapsulamento**: Detalhes de implementação são ocultados por interfaces limpas
   - **Extensibilidade**: Fácil adicionar novos tipos de extratores ou parsers

## Instalação

### Dependências

O projeto utiliza UV como gerenciador de pacotes e ambientes virtuais. Por isso, é necessário instalar o UV antes de instalar as dependências do projeto. Requisitos para dependências:

- Python 3.12 ou superior
- UV

### Instalação do UV

Para instalar o UV, siga os passos da [documentação oficial](https://docs.astral.sh/uv/getting-started/installation/).

### Configuração do Ambiente

Clone o repositório

```bash
git clone https://github.com/nf-scanner/nf-scanner-core.git
cd nf-scanner-core
```

Crie um ambiente virtual com UV

```bash
uv venv
```

Ative o ambiente virtual

```bash
# Linux/macOS
source .venv/bin/activate
```

Instale as dependências do projeto

```bash
uv pip install -e ".[dev]"
```

## Desenvolvimento

### Configuração de Variáveis de Ambiente

O projeto utiliza arquivos `.env` para gerenciar as chaves de API para integração com IA.

1. Crie um arquivo `.env` na raiz do projeto (você pode copiar o arquivo `env.example`)

```bash
cp env.example .env
```

2. Edite o arquivo `.env` e adicione suas chaves de API e outras configurações

```
CLAUDE_API_KEY=sua-chave-api-aqui
CLAUDE_API_ID=claude-sonnet-4-5-20250929
CLAUDE_API_ALIAS=claude-sonnet-4-5
```

3. A biblioteca carregará automaticamente as configurações do arquivo `.env`

```python
from nf_scanner_core.utils.config import get_ai_api_key

api_key = get_ai_api_key()
```

> **IMPORTANTE**: Nunca compartilhe ou comite o arquivo `.env` com suas chaves. O arquivo `.env` está incluído no `.gitignore`.

### Pré-commit hooks

O projeto utiliza pre-commit hooks para garantir a qualidade do código. Para configurá-los:

Instale as dependências de desenvolvimento

```bash
uv pip install -e ".[dev]"
```

Instale os hooks do pre-commit

```bash
pre-commit install
```

Os seguintes hooks serão executados automaticamente antes de cada commit:

- **Black**: Formata automaticamente o código Python
- **pytest**: Executa todos os testes do projeto

## Uso

### Extração de Dados de NFSe

#### Via linha de comando

```bash
# Extrai e processa dados de NFSe a partir de arquivo (PDF ou imagem)
nf-extract caminho/para/arquivo.pdf

# Opcionalmente, especifique um diretório de saída
nf-extract caminho/para/arquivo.pdf -o diretorio/saida
```

#### Via código Python

```python
from nf_scanner_core import NFExtractor

# Cria um extrator que automaticamente detecta o tipo de arquivo (PDF ou imagem)
extrator = NFExtractor("caminho/para/arquivo.pdf")  # ou .jpg, .png, etc.

# Extrai e obtém os dados estruturados
nfse = extrator.extract()
print(f"Número da NFSe: {nfse.numero_nfse}")
print(f"Valor total: {nfse.valores.valor_servicos}")

# Ou extrai e salva em formato JSON
json_path = extrator.extract_and_save()
print(f"Dados da NFSe salvos em: {json_path}")
```