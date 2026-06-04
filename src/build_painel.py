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
    ind_cols = [c for c in ind.columns if c not in ("municipio", "populacao_2022")]

    painel = (
        fem.merge(pop, on=["id_municipio", "ano"], how="left")
        .merge(ind[ind_cols], on="id_municipio", how="left")
    )

    painel["taxa_feminicidio_100k"] = painel["n_total"] / painel["populacao"] * 100_000
    painel["taxa_feminicidio_consumado_100k"] = (
        painel["n_consumado"] / painel["populacao"] * 100_000
    )

    ordem = [
        "id_municipio", "municipio", "ano",
        # desfecho (alvo)
        "n_total", "n_consumado", "n_tentativa",
        "taxa_feminicidio_100k", "taxa_feminicidio_consumado_100k",
        # exposição / denominador
        "populacao",
        # preditores socioeconômicos (fixos no município, ref. Censo 2022 / PIB)
        "pib_2022", "pib_2023", "pib_per_capita_2022",
        "taxa_alfabetizacao", "taxa_alfabetizacao_fem",
        "anos_medios_estudo", "anos_medios_estudo_fem",
    ]
    painel = painel[ordem].sort_values(["id_municipio", "ano"]).reset_index(drop=True)

    os.makedirs(FINAL, exist_ok=True)
    saida = os.path.join(FINAL, "painel_feminicidio_sp.csv")
    painel.to_csv(saida, index=False, encoding="utf-8-sig")

    print(f"Salvo: {saida}")
    print(f"Dimensão: {painel.shape}  (esperado 2580 x 16)")
    print("\nCobertura (não-nulos):")
    print(painel.notna().sum())
    print("\nPrévia:")
    print(painel.head(8).to_string(index=False))
    print("\nResumo taxa_feminicidio_100k:")
    print(painel["taxa_feminicidio_100k"].describe())


if __name__ == "__main__":
    main()
