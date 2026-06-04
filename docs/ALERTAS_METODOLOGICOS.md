# Alertas Metodológicos — leitura obrigatória antes da modelagem

Achados da auditoria técnica (verificados nos dados reais). Não são opiniões: são
divergências entre o que o relatório intermediário afirma e o que o pipeline efetivamente faz.

## 1. A base de "feminicídios" mistura CONSUMADO e TENTATIVA
`raw/ssp/feminicidios_2022_2025.csv` (1.636 casos) foi filtrada por
`DESCR_CONDUTA == "Feminicídio-contra a mulher por razões da condição de sexo feminino."`.
Distribuição por desfecho (`NATUREZA_APURADA`):

| Desfecho | Casos |
|---|---|
| TENTATIVA DE HOMICÍDIO | 1.136 |
| HOMICÍDIO DOLOSO (consumado) | 500 |

→ **~69% são tentativas.** O relatório descreve o objeto como feminicídio consumado
(Lei 13.104/2015, "homicídio doloso de mulher"). **Decidir e declarar** qual desfecho é o alvo.
O painel traz `n_total`, `n_consumado` e `n_tentativa` separados para permitir a escolha.

## 2. O campo de desfecho é inconsistente entre anos
Em **2022, 100% dos registros estão como "TENTATIVA DE HOMICIDIO"** (0 consumados), o que é
um artefato de preenchimento, não realidade. Logo, a série `n_consumado` por ano **não é comparável**:

| ano | n_consumado | n_tentativa | n_total |
|---|---|---|---|
| 2022 | 0 | 340 | 340 |
| 2023 | 201 | 140 | 341 |
| 2024 | 207 | 401 | 608 |
| 2025 | 92 | 255 | 347 |

→ Para uma série consumado-consistente, **revalidar a partir dos BOs brutos** (campo confiável) ou
usar a **contagem oficial da SSP** (`raw/ssp/api_dados.csv`, idDelito 134).

## 3. Filtro real ≠ filtro descrito no relatório
O relatório diz que a filtragem foi feita por `NATUREZA_APURADA` e `RUBRICA`.
Na prática (`limpeza.ipynb`) o filtro é por `DESCR_CONDUTA`. Em `RUBRICA`, 1.633 dos 1.636 são
"Homicídio (art. 121)" — ou seja, `RUBRICA` **não** isolaria feminicídios. Corrigir o texto.

## 4. Taxa: "por 100 mil mulheres" no relatório, mas população TOTAL no código
A fórmula implementada usa população **total** do município. Além disso,
`raw/ibge/populacao_municipio_SP.csv` **não tem desagregação por sexo** (só `populacao` total),
apesar de o relatório afirmar "desagregada por gênero".
**Decisão de projeto mantida:** usar população total. → Corrigir o texto e a fórmula no relatório
(trocar "mulheres" por "habitantes") ou obter a população feminina do IBGE.

## 5. 2025 está COMPLETO (12 meses), não "1º semestre"
O relatório diz "janeiro de 2022 a junho de 2025". Os dados têm os 12 meses de 2025 (347 casos).
Atualizar período para "2022–2025 (completo)".

## 6. O pico de 2024 (608) é o dobro dos demais anos (~340)
Com 2025 completo voltando a ~347, o salto de 2024 parece anômalo (mudança de classificação/cobertura).
Em painel, **efeitos fixos de ano** absorvem choques comuns; ainda assim, investigar antes de interpretar.

## 7. Muitos zeros — implicação para a modelagem
Só **334 dos 645 municípios** têm ≥1 caso. No painel município-ano, **642 de 2.580 células** têm ≥1 caso
(≈75% de zeros). Taxa bruta por 100 mil é instável em municípios pequenos (1 caso vira taxa enorme).
→ Preferir **modelos de contagem** (Poisson/Binomial Negativa) com `offset = log(população)`,
ou taxa suavizada (Bayes empírico), em vez de OLS sobre taxa crua.

## 8. Preditores socioeconômicos são fixos no tempo
PIB/alfabetização/anos de estudo têm referência 2022. No painel, não variam entre 2022–2025.
→ **Efeitos fixos de município não identificam** esses coeficientes. Usar pooled/between/efeitos
aleatórios, ou rodar como **cross-section** (colapsar para 1 linha por município).
