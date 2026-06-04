# PADRONIZAÇÃO DE COLUNAS - ANÁLISE E SOLUÇÃO

Pessoal, isso aqui é basicamente o processo inteiro que eu fiz para organizar as bases de dados, dado que todas estavam muito inconsistentes, algumas bases tinham certas coisas que outras nao tinham, ou os nomes eram altamente diferentes

## Problema Identificado
As bases de dados (2022-2025) tinham inconsistências em nomes de colunas:
1. Mesma coluna com nomes diferentes
2. Algumas colunas presentes apenas em 2024-2025
3. Problema de acentuação em 2025 (sem circunflexo)

## Solução Implementada

### 1. Mapeamento de Colunas Equivalentes
| Função | 2022 | 2023 | 2024 | 2025 | Padrão Final |
|--------|------|------|------|------|-------------|
| Período | DESCR_PERIODO | DESC_PERIODO | DESC_PERIODO | DESC_PERIODO | DESC_PERIODO |
| Município | CIDADE | NOME_MUNICIPIO | NOME_MUNICIPIO | NOME_MUNICIPIO | NOME_MUNICIPIO |
| Circunscritivo | CIRCUNSCRIÇÃO | CIRCUNSCRIÇÃO | CIRCUNSCRIÇÃO | CIRCUNSCRICAO | CIRCUNSCRICAO |

### 2. Colunas Novas (2024-2025)
- BTL
- CIA
- CMD
- COD IBGE

### 3. Colunas Inconsistentes
**2022 Não Tem:** DATA_REGISTRO, DESCR_SUBTIPOLOCAL
**2023 Não Tem:** DATA_COMUNICACAO_BO, DESCR_TIPOLOCAL
**2024 Não Tem:** DESCR_TIPOLOCAL
**2025 Não Tem:** COD IBGE

## Datasets Finais Disponíveis

### df_total (Todas as colunas)
- 4.792.971 linhas
- 29 colunas
- ⚠️ Contém NaN onde colunas faltam

### df_total_completo (Apenas colunas completas) ✓✓✓ RECOMENDADO
- 4.792.971 linhas
- 23 colunas (presentes em todos 4 anos)
- Sem NaN (dados 100% completos)

## Colunas Completas (df_total_completo)
1. ANO_BO
2. ANO_ESTATISTICA
3. BAIRRO
4. DATA_OCORRENCIA_BO
5. DESCR_CONDUTA
6. DESC_PERIODO
7. HORA_OCORRENCIA_BO
8. LATITUDE
9. LOGRADOURO
10. LONGITUDE
11. MES_ESTATISTICA
12. NATUREZA_APURADA
13. NOME_DELEGACIA
14. NOME_DELEGACIA_CIRCUNSCRICAO
15. NOME_DEPARTAMENTO
16. NOME_DEPARTAMENTO_CIRCUNSCRICAO
17. NOME_MUNICIPIO
18. NOME_MUNICIPIO_CIRCUNSCRICAO
19. NOME_SECCIONAL
20. NOME_SECCIONAL_CIRCUNSCRICAO
21. NUMERO_LOGRADOURO
22. NUM_BO
23. RUBRICA
