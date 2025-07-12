# Guia de Instalação

Este guia detalha os passos para instalar e configurar o Arco-Find em seu ambiente local.

## Pré-requisitos

Certifique-se de ter os seguintes softwares instalados em sua máquina:

* Python 3.8 ou superior
* Git

## Passos de Instalação

1. **Clone o Repositório:**

   ```bash
   git clone https://github.com/seu-usuario/arco-find.git
   cd arco-find
   ```

2. **Crie e Ative um Ambiente Virtual (Recomendado):**

   ```bash
   python -m venv .venv
   # No Windows
   .venv\Scripts\activate
   # No macOS/Linux
   source .venv/bin/activate
   ```

3. **Instale as Dependências:**

   ```bash
   pip install -r requirements.txt
   ```

O `requirements.txt` agora inclui `python-dotenv` para gerenciamento de variáveis de ambiente.

Após a instalação, você pode prosseguir para o [Guia de Configuração](configuration.md).
