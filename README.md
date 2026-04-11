# injexflow-v2# 🚀 InjexFlow 4.0 - Gestão Industrial & ISO 9001

Sistema de monitoramento de injetoras (Haitian Pluto) com foco em imutabilidade de dados e auditoria digital.

## 📂 Estrutura do Projeto

* **`main.py`**: Servidor API (FastAPI) que recebe dados do hardware/operador e gera o Hash SHA-256.
* **`app.py`**: Dashboard (Streamlit) para visualização de OEE, gráficos e exportação de relatórios Excel.
* **`teste_api.py`**: Script de simulação para testar a comunicação com a API.
* **`injexflow_industrial.db`**: Banco de dados SQLite (gerado automaticamente).

## 🛠️ Como Rodar o Projeto

### 1. Instalar Dependências
Abra o terminal na pasta do projeto e rode:
```bash
pip install fastapi uvicorn streamlit pandas requests xlsxwriter