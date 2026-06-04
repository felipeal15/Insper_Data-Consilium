# Dicionário de Dados — `final/painel_feminicidio_sp.csv`

Painel **município × ano**. 645 municípios × 4 anos (2022–2025) = **2.580 linhas**.
Unidade de observação: um município em um ano.

| Coluna | Tipo | Varia por ano? | Descrição |
|---|---|---|---|
| `id_municipio` | int | — | Código IBGE de 7 dígitos. Chave primária junto com `ano`. |
| `municipio` | str | — | Nome oficial do município. |
| `ano` | int | sim | 2022, 2023, 2024 ou 2025. |
| `n_total` | int | sim | Registros de feminicídio (consumado + tentativa) no município-ano. **Inclui tentativas.** |
| `n_consumado` | int | sim | Subconjunto com `NATUREZA_APURADA = "HOMICÍDIO DOLOSO"`. ⚠️ Não confiável em 2022 (ver alertas). |
| `n_tentativa` | int | sim | Subconjunto classificado como tentativa. |
| `taxa_feminicidio_100k` | float | sim | `n_total / populacao × 100.000`. **Denominador = população TOTAL** (decisão de projeto). |
| `taxa_feminicidio_consumado_100k` | float | sim | Idem, usando `n_consumado`. |
| `populacao` | int | sim | População total do município no ano (IBGE). |
| `pib_2022` | float | não | PIB municipal a preços correntes de 2022 (R$). |
| `pib_2023` | float | não | PIB municipal a preços correntes de 2023 (R$). |
| `pib_per_capita_2022` | float | não | `pib_2022 / populacao_2022` (R$/hab). |
| `taxa_alfabetizacao` | float | não | Alfabetizados / população 15+ (Censo 2022). 0–1. |
| `taxa_alfabetizacao_fem` | float | não | Idem, só mulheres. |
| `anos_medios_estudo` | float | não | Anos médios de estudo, pessoas 11+ (Censo 2022). |
| `anos_medios_estudo_fem` | float | não | Idem, só mulheres. |

## Variáveis que NÃO variam no tempo

Os blocos de PIB, alfabetização e anos de estudo têm referência **Censo 2022 / PIB 2022–2023** e
entram no painel **constantes** ao longo dos 4 anos. Na prática, o painel tem:
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
`id_municipio, municipio, populacao_2022, pib_2022, pib_2023, pib_per_capita_2022,`
`taxa_alfabetizacao, taxa_alfabetizacao_fem, anos_medios_estudo, anos_medios_estudo_fem` — 1 linha/município.
