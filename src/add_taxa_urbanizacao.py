"""
add_taxa_urbanizacao.py
=========================
Adiciona a coluna `taxa_urbanizacao_pct` em `final/painel_feminicidio_sp.csv`.

Fonte: raw/socioeconomicos/domicilios_situacao_domicilio_municipios_sp.csv
       (SIDRA 9922, Censo 2022 — domicílios particulares permanentes ocupados)

Cálculo por município:
  taxa_urbanizacao_pct = (domicílios urbanos / domicílios totais) × 100

O indicador é invariante no tempo (Censo 2022) e replicado em todas as linhas
do painel município × ano do mesmo município.

Uso: python src/add_taxa_urbanizacao.py
"""
from __future__ import annotations

import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_SOCIO = os.path.join(ROOT, "raw", "socioeconomicos")
FINAL = os.path.join(ROOT, "final")

DOMICILIOS_PATH = os.path.join(
    RAW_SOCIO, "domicilios_situacao_domicilio_municipios_sp.csv"
)
PAINEL_PATH = os.path.join(FINAL, "painel_feminicidio_sp.csv")


def carregar_taxa_urbanizacao() -> pd.DataFrame:
    dom = pd.read_csv(DOMICILIOS_PATH, dtype={"codigo_municipio": str})
    dom["valor"] = pd.to_numeric(dom["valor"], errors="coerce")
    dom = dom.dropna(subset=["valor"])

    wide = dom.pivot_table(
        index="codigo_municipio",
        columns="situacao_domicilio",
        values="valor",
        aggfunc="first",
    )
    if "Urbana" not in wide.columns or "Total" not in wide.columns:
        raise ValueError(
            "Base de domicílios deve conter as categorias 'Urbana' e 'Total'."
        )

    out = wide[["Urbana", "Total"]].rename(
        columns={"Urbana": "domicilios_urbanos", "Total": "domicilios_total"}
    )
    out["taxa_urbanizacao_pct"] = (
        out["domicilios_urbanos"] / out["domicilios_total"] * 100
    )
    return (
        out.reset_index()
        .rename(columns={"codigo_municipio": "id_municipio"})
        .assign(id_municipio=lambda d: pd.to_numeric(d["id_municipio"]))
        [["id_municipio", "taxa_urbanizacao_pct"]]
    )


def main() -> None:
    if not os.path.isfile(PAINEL_PATH):
        raise FileNotFoundError(
            f"Painel não encontrado: {PAINEL_PATH}. Execute build_painel.py antes."
        )

    painel = pd.read_csv(PAINEL_PATH)
    taxa = carregar_taxa_urbanizacao()

    if "taxa_urbanizacao_pct" in painel.columns:
        painel = painel.drop(columns=["taxa_urbanizacao_pct"])

    painel = painel.merge(taxa, on="id_municipio", how="left")

    faltam = painel[painel["taxa_urbanizacao_pct"].isna()]["id_municipio"].nunique()
    if faltam:
        ids = painel.loc[painel["taxa_urbanizacao_pct"].isna(), "id_municipio"].unique()
        print(f"[aviso] {faltam} município(s) sem taxa de urbanização: {ids}")

    cols = list(painel.columns)
    cols.remove("taxa_urbanizacao_pct")
    cols.append("taxa_urbanizacao_pct")
    painel = painel[cols].sort_values(["id_municipio", "ano"]).reset_index(drop=True)

    painel.to_csv(PAINEL_PATH, index=False, encoding="utf-8-sig")

    print(f"Salvo: {PAINEL_PATH}")
    print(f"Dimensão: {painel.shape}")
    print(f"Municípios com taxa: {painel.groupby('id_municipio')['taxa_urbanizacao_pct'].first().notna().sum()}")
    print("\nResumo taxa_urbanizacao_pct:")
    print(painel.groupby("id_municipio")["taxa_urbanizacao_pct"].first().describe())


if __name__ == "__main__":
    main()
