# Dicionário de Dados — `final/painel_feminicidio_sp.csv`

Painel **município × ano**. 645 municípios × 4 anos (2022–2025) = **2.580 linhas × 14 colunas**.
Unidade de observação: um município em um ano.

**Decisões de projeto (Fase 0, encerradas):** desfecho **principal = consumado**
(`taxa_feminicidio_consumado_100k`); **robustez = total** (`taxa_feminicidio_total_100k`).
A taxa é sempre normalizada pela **população TOTAL** do município (não feminina).

| Coluna | Tipo | Varia por ano? | Descrição |
|---|---|---|---|
| `id_municipio` | int | — | Código IBGE de 7 dígitos. Chave primária junto com `ano`. |
| `municipio` | str | — | Nome oficial do município. |
| `ano` | int | sim | 2022, 2023, 2024 ou 2025. |
| `n_consumado` | int | sim | Feminicídios consumados (`NATUREZA_APURADA = "HOMICÍDIO DOLOSO"`). **Desfecho principal.** ⚠️ Não confiável em 2022 (ver alertas). |
| `n_total` | int | sim | Consumado + tentativa no município-ano. **Inclui tentativas** (~69% do total). Desfecho de robustez. |
| `n_tentativa` | int | sim | Subconjunto classificado como tentativa. |
| `taxa_feminicidio_consumado_100k` | float | sim | **PRINCIPAL.** `n_consumado / populacao × 100.000`. Denominador = população TOTAL. |
| `taxa_feminicidio_total_100k` | float | sim | **ROBUSTEZ.** `n_total / populacao × 100.000`. Denominador = população TOTAL. |
| `populacao` | int | sim | População total do município no ano (IBGE). |
| `pib_per_capita_2022` | float | não | `pib_2022 / populacao_2022` (R$/hab). Censo/PIB 2022. |
| `taxa_alfabetizacao` | float | não | Alfabetizados / população 15+ (Censo 2022, SIDRA 9542). 0–1. |
| `anos_medios_estudo` | float | não | Anos médios de estudo, pessoas 11+ (Censo 2022, SIDRA 10062). |
| `pct_ensino_medio` | float | não | % da população 18+ com ensino médio completo **ou mais** (Censo 2022, SIDRA 10061). 0–1. |
| `pct_ensino_superior` | float | não | % da população 18+ com ensino superior completo (Censo 2022, SIDRA 10061). 0–1. |

> **Descartados** (para evitar redundância): recortes femininos de educação
> (`*_fem`, r≈0,97 com o total), `pib_2023` (r≈0,9998 com `pib_2022`) e o recorte por
> raça (ausente nos CSVs SIDRA baixados). ⚠️ `anos_medios_estudo` e `pct_ensino_medio`
> são fortemente colineares (r≈0,94) — na modelagem, preferir um dos dois.

## Variáveis que NÃO variam no tempo

Os blocos de PIB, alfabetização, anos de estudo e nível de escolaridade têm referência
**Censo 2022 / PIB 2022** e entram no painel **constantes** ao longo dos 4 anos. Na prática, o painel tem:
- **variação temporal** apenas em `n_*`, `taxa_*` e `populacao`;
- **variação transversal** (entre municípios) em todos os preditores.

Isso tem implicação direta na modelagem (ver `docs/ALERTAS_METODOLOGICOS.md` e a Parte 6 da auditoria):
um modelo de **efeitos fixos de município** absorveria todos os preditores socioeconômicos (eles são
fixos no município) e não os estimaria. Para identificar o efeito socioeconômico, usar
**pooled OLS / efeitos aleatórios / between**, ou tratar o problema como **cross-section** (1 linha por município).

## Arquivos `processed/`

### `feminicidios_municipio_ano.csv`
`id_municipio, municipio, ano, n_consumado, n_tentativa, n_outro, n_total` — grid completo com zeros.

### `indicadores_municipais.csv`
`id_municipio, municipio, populacao_2022, pib_2022, pib_per_capita_2022,`
`taxa_alfabetizacao, anos_medios_estudo, pct_ensino_medio, pct_ensino_superior` — 1 linha/município (645).
