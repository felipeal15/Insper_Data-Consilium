# Feminicídio no Estado de São Paulo
### Insper Data × Consilium — Pesquisa 2026.1

> **Pergunta de pesquisa:** Quais fatores socioeconômicos afetam o índice de feminicídio nos municípios do estado de São Paulo?

Projeto de pesquisa quantitativa desenvolvido em parceria entre o **Insper Data** (laboratório de análise de dados) e o **Consilium** (observatório de políticas públicas), com orientação da **Profa. Dra. Maria Kelly Venezuela** (Estatística, USP).

---

## Sobre o Projeto

A pesquisa parte de 4,8 milhões de boletins de ocorrência registrados pela SSP-SP entre 2022 e 2025, dos quais 1.636 foram identificados como feminicídio. O objetivo é construir indicadores municipais normalizados e, a partir deles, investigar associações entre características socioeconômicas dos municípios e suas taxas de feminicídio, gerando insumos para políticas públicas.

O trabalho está organizado em cinco etapas sequenciais:

```
Coleta → Integração → Limpeza/Padronização → Análise Exploratória → Modelagem Estatística
```

---

## Estrutura do Repositório

```
.
├── limpeza.ipynb                          # Pipeline principal: integração e padronização das bases
├── analise_feminicidios_ref.ipynb         # Filtragem dos casos e análise exploratória
├── preparar_populacao_municipios_sp.ipynb # Processamento dos dados de população (IBGE)
├── api.ipynb                              # Consultas e integrações via API
├── padronizar_colunas.py                  # Módulo de padronização de colunas entre anos
├── municipio_sp.py                        # Utilitários para manipulação de municípios SP
├── csvs/                                  # Outputs gerados (bases consolidadas)
│   ├── feminicidios_2022_2025.csv         # 1.636 casos filtrados, 23 variáveis completas
│   └── populacao_municipio_SP_media_2022_2025.csv
├── DOCUMENTACAO_COLUNAS.md               # Dicionário de dados e mapeamento de colunas
├── requirements.txt
└── README.md
```

---

## Dados

| Fonte | Descrição | Período |
|---|---|---|
| SSP-SP (Boletins de Ocorrência) | ~4,8 milhões de registros criminais | Jan 2022 – Dez 2025 |
| IBGE (Estimativas de População) | População por município e gênero | 2022–2025 |

Os dados brutos da SSP-SP **não estão versionados** por volume. Para obtê-los, acesse o [portal de dados abertos da SSP-SP](https://www.ssp.sp.gov.br/estatistica/consultas).

---

## Como Rodar

### Pré-requisitos

- Python 3.10+
- VS Code (recomendado) com extensão Jupyter

### 1. Clonar o repositório

```bash
git clone https://github.com/felipeal15/Insper_Data-Consilium.git
cd Insper_Data-Consilium
```

### 2. Criar e ativar ambiente virtual

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name insper-data-consilium --display-name "Python (insper-data-consilium)"
```

### 4. Ordem de execução dos notebooks

Execute nesta sequência para reproduzir o pipeline completo:

1. `limpeza.ipynb` — integra e padroniza os 7 arquivos semestrais
2. `preparar_populacao_municipios_sp.ipynb` — processa dados populacionais do IBGE
3. `analise_feminicidios_ref.ipynb` — filtra feminicídios e gera análise exploratória

---

## Principais Resultados (Etapa Descritiva)

- **1.636 casos** de feminicídio identificados no período (Jan 2022 – Dez 2025)
- **2024** apresenta pico expressivo com 608 ocorrências, salto de ~78% sobre 2023
- Após normalização por população feminina, o município de **São Paulo cai da 1ª para a ~300ª posição** no ranking — municípios do Interior e da DEMACRO lideram em taxa por 100 mil mulheres
- O **Interior concentra mais de 60%** dos casos em todos os anos analisados

---

## Próximas Etapas

- [ ] Integração das bases socioeconômicas complementares (IBGE, Atlas Brasil)
- [ ] Definição do modelo de regressão com orientação da Profa. Kelly Venezuela
- [ ] Modelagem estatística e comparação com hipóteses teóricas
- [ ] Construção do mapa interativo municipal

---

## Equipe

| Nome | Entidade |
|---|---|
| Beatriz Telles Feldberg | Insper Data |
| Felipe Aldrighi de Lima | Insper Data |
| Henrique Almeida Barcelos | Insper Data |
| Yamandú Germano Cavalcanti | Insper Data |
| Lucas Pires Castanho | Consilium |
| Matheus Tahan Cunha | Consilium |

**Orientadora:** Profa. Dra. Maria Kelly Venezuela — Estatística (USP), docente no Insper

---

## Referências Teóricas

- Shaw & McKay (1942) — Teoria da Desorganização Social
- Cohen & Felson (1979) — Teoria da Atividade de Rotina
- Sepúlveda et al. (2018) — Heterogeneidade espacial do feminicídio em Antioquia, Colômbia
- Souza Lima (2025) — Análise espacial do feminicídio no município de São Paulo
- Lei nº 13.104/2015 — Define feminicídio como crime hediondo no Brasil
