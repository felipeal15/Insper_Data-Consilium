# Pipeline de Dados — Feminicídio SP

Fluxo de dados em três camadas: `raw/` → `processed/` → `final/`.
Todo o código de construção está em `src/`.

```
raw/                                  (entradas — não derivadas)
├── ssp/
│   ├── feminicidios_2022_2025.csv    1.636 casos (nível BO) filtrados da base da SSP-SP
│   └── api_dados.csv                 contagem oficial SSP (API, idDelito 134) por ano/mês/região
├── ibge/
│   └── populacao_municipio_SP.csv    população por município e ano (2022-2025) — TOTAL
└── socioeconomicos/
    ├── alfabetizacao.csv             SIDRA 9542 (Censo 2022) — alfabetização 15+
    ├── anos_estudos.csv              SIDRA 10062 (Censo 2022) — anos médios de estudo 11+
    ├── nivel-escolaridade.csv        SIDRA 10061 (Censo 2022) — pessoas 18+ por nível de instrução
    └── pib_municipal.csv             PIB municipal a preços correntes (2002-2023)

processed/                            (derivados intermediários — 1 chave clara cada)
├── indicadores_municipais.csv        645 municípios × indicadores socioeconômicos (fixos, ref. 2022)
├── feminicidios_municipio_ano.csv    645 mun. × 4 anos = 2.580 linhas (contagens, com zeros)
└── populacao_municipio_SP_media_2022_2025.csv   (legado — usado pela EDA antiga)

final/
└── painel_feminicidio_sp.csv         2.580 linhas (645 × 4) — DATASET DE MODELAGEM
```

## Como reconstruir tudo

```bash
python src/run_pipeline.py
```

Ou etapa a etapa (mesma ordem):

```bash
python src/build_indicadores_municipais.py      # -> processed/indicadores_municipais.csv
python src/build_feminicidios_municipio_ano.py  # -> processed/feminicidios_municipio_ano.csv
python src/build_painel.py                       # -> final/painel_feminicidio_sp.csv
```

## Chaves de junção

| Junção | Chave |
|---|---|
| PIB ↔ população | `id_municipio` (= `Cod_mun`, código IBGE 7 dígitos) — direto |
| alfabetização / anos_estudo / nível-escolaridade ↔ população | nome canônico (`chave_municipio_oficial`) → `id_municipio` |
| feminicídios (BO) ↔ população | nome do BO (`chave_nome_bo`) → `id_municipio` |
| painel | `id_municipio` + `ano` (socioeconômico entra constante no município) |

O mapeamento textual de nomes está em `src/municipio_sp.py`
(funções `chave_municipio_oficial` e `chave_nome_bo` + dicionário de aliases).
A construção dos indicadores tem um dicionário extra `ALIASES_SIDRA` para divergências de grafia do SIDRA.

## Camada raw da SSP

A base completa de ~4,8 milhões de BOs (`Bases/csv/*.csv`) **não é versionada** (volume; vive no Google Drive).
O notebook `limpeza.ipynb` consome esses arquivos e produz `raw/ssp/feminicidios_2022_2025.csv`,
que é o recorte versionado e ponto de entrada público do pipeline.
