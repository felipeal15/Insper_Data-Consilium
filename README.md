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

Pipeline de dados em três camadas (`raw/` → `processed/` → `final/`); código em `src/`.

```
.
├── raw/                                   # Entradas (não derivadas)
│   ├── ssp/
│   │   ├── feminicidios_2022_2025.csv     # 1.636 casos (nível BO), 23 variáveis completas
│   │   └── api_dados.csv                  # Contagem oficial SSP (API) por ano/mês/região
│   ├── ibge/
│   │   └── populacao_municipio_SP.csv     # População por município e ano (2022-2025)
│   └── socioeconomicos/
│       ├── alfabetizacao.csv              # SIDRA 9542 (Censo 2022)
│       ├── anos_estudos.csv               # SIDRA 10062 (Censo 2022)
│       └── pib_municipal.csv              # PIB municipal (2002-2023)
├── processed/                             # Derivados intermediários
│   ├── indicadores_municipais.csv         # 645 municípios × indicadores socioeconômicos
│   ├── feminicidios_municipio_ano.csv     # 645 × 4 anos = 2.580 linhas (contagens c/ zeros)
│   └── populacao_municipio_SP_media_2022_2025.csv
├── final/
│   └── painel_feminicidio_sp.csv          # DATASET DE MODELAGEM (2.580 × 16)
├── src/                                   # Código do pipeline
│   ├── municipio_sp.py                    # Chaves de cruzamento de nomes de município
│   ├── padronizar_colunas.py              # Padronização de colunas entre anos (SSP)
│   ├── build_indicadores_municipais.py
│   ├── build_feminicidios_municipio_ano.py
│   ├── build_painel.py
│   └── run_pipeline.py                    # Orquestrador (roda os 3 acima na ordem)
├── limpeza.ipynb                          # (legado) integração/padronização dos BOs brutos
├── analise_feminicidios_ref.ipynb         # (legado) análise exploratória / gráficos
├── preparar_populacao_municipios_sp.ipynb # (legado) média populacional
├── api.ipynb                              # Coleta da contagem oficial via API da SSP
├── reports/                               # Relatório e figuras
│   ├── relatorio_feminicidio_sp.qmd / .pdf
│   └── img_dos_graficos/
├── docs/
│   ├── PIPELINE.md                        # Fluxo de dados e como reconstruir
│   ├── DICIONARIO_PAINEL.md               # Dicionário do dataset final
│   ├── ALERTAS_METODOLOGICOS.md           # ⚠️ Ler antes de modelar
│   └── DOCUMENTACAO_COLUNAS.md            # Mapeamento de colunas entre anos
├── requirements.txt
└── README.md
```

> ⚠️ **Antes de modelar, leia [docs/ALERTAS_METODOLOGICOS.md](docs/ALERTAS_METODOLOGICOS.md).**
> Pontos críticos: a base mistura feminicídio **consumado e tentativa**; a taxa usa população
> **total** (não feminina); e os preditores socioeconômicos são **fixos no tempo** (Censo 2022).

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

### 4. Reconstruir as bases derivadas

Com as entradas em `raw/` já versionadas, o pipeline regenera `processed/` e `final/`:

```bash
python src/run_pipeline.py
```

Para reprocessar a base bruta da SSP (~4,8 mi de BOs, no Google Drive) e a EDA, execute os
notebooks legados nesta ordem (rodando a partir da raiz do repositório):

1. `limpeza.ipynb` — integra/padroniza os arquivos semestrais → `raw/ssp/feminicidios_2022_2025.csv`
2. `preparar_populacao_municipios_sp.ipynb` — média populacional → `processed/`
3. `analise_feminicidios_ref.ipynb` — análise exploratória e gráficos

> Detalhes do fluxo em [docs/PIPELINE.md](docs/PIPELINE.md).

---

## Principais Resultados (Etapa Descritiva)

- **1.636 casos** de feminicídio identificados no período (Jan 2022 – Dez 2025)
- **2024** apresenta pico expressivo com 608 ocorrências, salto de ~78% sobre 2023
- Após normalização por população feminina, o município de **São Paulo cai da 1ª para a ~300ª posição** no ranking — municípios do Interior e da DEMACRO lideram em taxa por 100 mil mulheres
- O **Interior concentra mais de 60%** dos casos em todos os anos analisados

---

## Próximas Etapas

- [x] Integração das bases socioeconômicas (PIB, alfabetização, anos de estudo) → `final/painel_feminicidio_sp.csv`
- [ ] Correção das inconsistências do relatório (ver `docs/ALERTAS_METODOLOGICOS.md`)
- [ ] Definição do modelo de regressão com orientação da Profa. Kelly Venezuela
- [ ] Modelagem estatística (contagem/painel) e comparação com hipóteses teóricas
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
