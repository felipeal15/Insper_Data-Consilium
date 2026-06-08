"""
build_painel.py
===============
Monta o dataset final de modelagem `final/painel_feminicidio_sp.csv`
no formato PAINEL município x ano (645 x 4 = 2.580 linhas).

Junta:
  processed/feminicidios_municipio_ano.csv   (desfecho, varia por ano)
  raw/ibge/populacao_municipio_SP.csv         (população, varia por ano)
  processed/indicadores_municipais.csv        (socioeconômico, fixo no município)

DECISÃO DE PROJETO (mantida): a taxa é normalizada pela POPULAÇÃO TOTAL do
município (não pela população feminina). Ver alerta no relatório/documentação.

Uso: python src/build_painel.py
"""
from __future__ import annotations

import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_IBGE = os.path.join(ROOT, "raw", "ibge")
PROCESSED = os.path.join(ROOT, "processed")
FINAL = os.path.join(ROOT, "final")
ANOS = [2022, 2023, 2024, 2025]


def main() -> None:
    fem = pd.read_csv(os.path.join(PROCESSED, "feminicidios_municipio_ano.csv"))
    pop = pd.read_csv(os.path.join(RAW_IBGE, "populacao_municipio_SP.csv"))
    pop = pop[pop["ano"].isin(ANOS)][["id_municipio", "ano", "populacao"]]
    ind = pd.read_csv(os.path.join(PROCESSED, "indicadores_municipais.csv"))
    # Preditores socioeconômicos levados ao painel (conjunto enxuto, ref. Censo 2022).
    PREDITORES = [
        "pib_per_capita_2022",
        "taxa_alfabetizacao",
        "anos_medios_estudo",
        "pct_ensino_medio",
        "pct_ensino_superior",
    ]
    painel = (
        fem.merge(pop, on=["id_municipio", "ano"], how="left")
        .merge(ind[["id_municipio", *PREDITORES]], on="id_municipio", how="left")
    )

    # DECISÃO DE PROJETO (Fase 0): taxa normalizada pela POPULAÇÃO TOTAL (não feminina).
    # Desfecho PRINCIPAL = consumado; total (consumado + tentativa) = robustez.
    painel["taxa_feminicidio_consumado_100k"] = (
        painel["n_consumado"] / painel["populacao"] * 100_000
    )
    painel["taxa_feminicidio_total_100k"] = (
        painel["n_total"] / painel["populacao"] * 100_000
    )

    ordem = [
        "id_municipio", "municipio", "ano",
        # contagens (para modelos de contagem: Poisson/BinNeg com offset log-pop)
        "n_consumado", "n_total", "n_tentativa",
        # taxas por 100 mil habitantes — consumado = principal, total = robustez
        "taxa_feminicidio_consumado_100k", "taxa_feminicidio_total_100k",
        # exposição / denominador
        "populacao",
        # preditores socioeconômicos (fixos no município, ref. Censo 2022)
        *PREDITORES,
    ]
    painel = painel[ordem].sort_values(["id_municipio", "ano"]).reset_index(drop=True)

    os.makedirs(FINAL, exist_ok=True)
    saida = os.path.join(FINAL, "painel_feminicidio_sp.csv")
    painel.to_csv(saida, index=False, encoding="utf-8-sig")

    print(f"Salvo: {saida}")
    print(f"Dimensão: {painel.shape}  (esperado 2580 x 14)")
    print("\nCobertura (não-nulos):")
    print(painel.notna().sum())
    print("\nPrévia:")
    print(painel.head(8).to_string(index=False))
    print("\nResumo taxa_feminicidio_consumado_100k (principal):")
    print(painel["taxa_feminicidio_consumado_100k"].describe())


if __name__ == "__main__":
    main()
