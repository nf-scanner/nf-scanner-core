# nf-scanner-core
Biblioteca para leitura de notas fiscais.

## Funcionalidades

- **Extração de Texto de PDFs**: Extrai o texto completo de arquivos PDF utilizando a biblioteca PyMuPDF.

## Instalação

### Dependências

O projeto utiliza UV como gerenciador de pacotes e ambientes virtuais. Por isso, é necessário instalar o UV antes de instalar as dependências do projeto. Requisitos para dependências:

- Python 3.12 ou superior
- UV

### Instalação do UV

Para instalar o UV, siga os passos da [documentação oficial](https://docs.astral.sh/uv/getting-started/installation/).

### Configuração do Ambiente

1. Clone o repositório
```bash
git clone https://github.com/nf-scanner/nf-scanner-core.git
cd nf-scanner-core
```

2. Crie um ambiente virtual com UV
```bash
uv venv
```

3. Ative o ambiente virtual
```bash
# Linux/macOS
source .venv/bin/activate
```

4. Instale as dependências do projeto
```bash
uv pip install -e ".[dev]"
```

## Desenvolvimento

### Pré-commit hooks

O projeto utiliza pre-commit hooks para garantir a qualidade do código. Para configurá-los:

1. Instale as dependências de desenvolvimento
```bash
uv pip install -e ".[dev]"
```

2. Instale os hooks do pre-commit
```bash
pre-commit install
```

Os seguintes hooks serão executados automaticamente antes de cada commit:
- **Black**: Formata automaticamente o código Python
- **pytest**: Executa todos os testes do projeto

## Uso

### Extração de Texto de PDFs

#### Via linha de comando

```bash
# Extrai o texto do PDF
nf-extract caminho/para/arquivo.pdf
```

#### Via código Python

```python
from nf_scanner_core.pdf_extractor import extract_text_from_pdf

# Extrai o texto do PDF
texto = extract_text_from_pdf("caminho/para/arquivo.pdf")

print(texto)
```