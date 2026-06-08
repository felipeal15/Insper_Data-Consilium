"""
add_taxa_saneamento.py
======================
Adiciona a coluna `taxa_saneamento_basico_pct` em `final/painel_feminicidio_sp.csv`.

Fonte: raw/socioeconomicos/domicilios_rede_agua_municipios_sp.csv
       (SIDRA 6803, Censo 2022 — ligação à rede geral de distribuição de água)

Cálculo por município (Opção A):
  taxa_saneamento_basico_pct =
      (domicílios com rede como forma principal / domicílios totais) × 100

O indicador é invariante no tempo (Censo 2022) e replicado em todas as linhas
do painel município × ano do mesmo município.

Uso: python src/add_taxa_saneamento.py
"""
from __future__ import annotations

import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_SOCIO = os.path.join(ROOT, "raw", "socioeconomicos")
FINAL = os.path.join(ROOT, "final")

REDE_AGUA_PATH = os.path.join(
    RAW_SOCIO, "domicilios_rede_agua_municipios_sp.csv"
)
PAINEL_PATH = os.path.join(FINAL, "painel_feminicidio_sp.csv")

CAT_REDE_PRINCIPAL = (
    "Possui ligação à rede geral e a utiliza como forma principal"
)


def carregar_taxa_saneamento() -> pd.DataFrame:
    dom = pd.read_csv(REDE_AGUA_PATH, dtype={"codigo_municipio": str})
    dom["valor"] = pd.to_numeric(dom["valor"], errors="coerce")
    dom = dom.dropna(subset=["valor"])

    wide = dom.pivot_table(
        index="codigo_municipio",
        columns="categoria_rede_agua",
        values="valor",
        aggfunc="first",
    )
    if CAT_REDE_PRINCIPAL not in wide.columns or "Total" not in wide.columns:
        raise ValueError(
            f"Base de domicílios deve conter '{CAT_REDE_PRINCIPAL}' e 'Total'."
        )

    out = wide[[CAT_REDE_PRINCIPAL, "Total"]].rename(
        columns={
            CAT_REDE_PRINCIPAL: "domicilios_rede_principal",
            "Total": "domicilios_total",
        }
    )
    out["taxa_saneamento_basico_pct"] = (
        out["domicilios_rede_principal"] / out["domicilios_total"] * 100
    )
    return (
        out.reset_index()
        .rename(columns={"codigo_municipio": "id_municipio"})
        .assign(id_municipio=lambda d: pd.to_numeric(d["id_municipio"]))
        [["id_municipio", "taxa_saneamento_basico_pct"]]
    )


def main() -> None:
    if not os.path.isfile(PAINEL_PATH):
        raise FileNotFoundError(
            f"Painel não encontrado: {PAINEL_PATH}. Execute build_painel.py antes."
        )

    painel = pd.read_csv(PAINEL_PATH)
    taxa = carregar_taxa_saneamento()

    if "taxa_saneamento_basico_pct" in painel.columns:
        painel = painel.drop(columns=["taxa_saneamento_basico_pct"])

    painel = painel.merge(taxa, on="id_municipio", how="left")

    faltam = painel[painel["taxa_saneamento_basico_pct"].isna()]["id_municipio"].nunique()
    if faltam:
        ids = painel.loc[
            painel["taxa_saneamento_basico_pct"].isna(), "id_municipio"
        ].unique()
        print(f"[aviso] {faltam} município(s) sem taxa de saneamento: {ids}")

    cols = list(painel.columns)
    cols.remove("taxa_saneamento_basico_pct")
    cols.append("taxa_saneamento_basico_pct")
    painel = painel[cols].sort_values(["id_municipio", "ano"]).reset_index(drop=True)

    painel.to_csv(PAINEL_PATH, index=False, encoding="utf-8-sig")

    print(f"Salvo: {PAINEL_PATH}")
    print(f"Dimensão: {painel.shape}")
    print(
        "Municípios com taxa:",
        painel.groupby("id_municipio")["taxa_saneamento_basico_pct"]
        .first()
        .notna()
        .sum(),
    )
    print("\nResumo taxa_saneamento_basico_pct:")
    print(
        painel.groupby("id_municipio")["taxa_saneamento_basico_pct"]
        .first()
        .describe()
    )


if __name__ == "__main__":
    main()
