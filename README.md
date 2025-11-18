# nf-scanner-core
Biblioteca para leitura de notas fiscais.

## Instalação

### Pré-requisitos

O projeto utiliza UV como gerenciador de pacotes e ambientes virtuais. Por isso, é necessário instalar o UV antes de instalar as dependências do projeto. Dependências diretas:

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
uv pip install -e .
```