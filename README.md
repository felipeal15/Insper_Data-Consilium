# Insper-Data-Consilium

Pesquisa 2026.1

## Como rodar em outro computador

Este projeto depende de bibliotecas Python para o notebook `limpeza.ipynb`.

### 1) Criar e ativar ambiente virtual

No PowerShell (Windows):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Instalar dependencias

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name insper-data-consilium --display-name "Python (insper-data-consilium)"
```

### 3) Abrir o notebook

1. Abra `limpeza.ipynb` no VS Code.
2. Selecione o kernel `Python (insper-data-consilium)`.
3. Execute as celulas em ordem.

## Estrutura

- `limpeza.ipynb`: notebook principal de limpeza e consolidacao.
- `padronizar_colunas.py`: utilitarios para padronizacao de colunas.
- `Bases/csv/`: bases semestrais 2022-2025.
