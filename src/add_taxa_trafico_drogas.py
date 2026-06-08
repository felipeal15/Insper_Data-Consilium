"""
add_taxa_trafico_drogas.py
==========================
Adiciona a coluna `taxa_trafico_drogas_100k` em `final/painel_feminicidio_sp.csv`.

Fonte: raw/ssp/trafico_drogas_2022_2025.csv
População: coluna `populacao` já presente no painel (raw/ibge/populacao_municipio_SP.csv)

Cálculo por município × ano (mesma lógica de build_painel.py para feminicídio):
  taxa_trafico_drogas_100k = (n_bos_trafico / populacao) × 100_000

Pré-requisito: python src/build_trafico_drogas_ssp.py

Uso: python src/add_taxa_trafico_drogas.py
"""
from __future__ import annotations

import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from municipio_sp import chave_municipio_oficial, chave_nome_bo  # noqa: E402

RAW_SSP = os.path.join(ROOT, "raw", "ssp")
RAW_IBGE = os.path.join(ROOT, "raw", "ibge")
FINAL = os.path.join(ROOT, "final")

TRAFICO_PATH = os.path.join(RAW_SSP, "trafico_drogas_2022_2025.csv")
PAINEL_PATH = os.path.join(FINAL, "painel_feminicidio_sp.csv")
ANOS = [2022, 2023, 2024, 2025]


def carregar_contagens() -> pd.DataFrame:
    pop = pd.read_csv(os.path.join(RAW_IBGE, "populacao_municipio_SP.csv"))
    cw = (
        pop[["id_municipio", "municipio"]]
        .drop_duplicates()
        .assign(chave=lambda d: d["municipio"].map(chave_municipio_oficial))
    )

    traf = pd.read_csv(TRAFICO_PATH, encoding="utf-8-sig")
    traf = traf.dropna(subset=["NOME_MUNICIPIO", "ANO_ESTATISTICA"]).copy()
    traf["ano"] = traf["ANO_ESTATISTICA"].astype(int)
    traf["chave"] = traf["NOME_MUNICIPIO"].astype(str).str.strip().map(chave_nome_bo)
    traf = traf.merge(cw[["id_municipio", "chave"]], on="chave", how="left")

    sem_id = traf["id_municipio"].isna().sum()
    if sem_id:
        chaves = sorted(traf.loc[traf["id_municipio"].isna(), "chave"].unique())
        print(f"[aviso] {sem_id} BOs sem id_municipio. Chaves: {chaves[:20]}")
    traf = traf.dropna(subset=["id_municipio"])
    traf["id_municipio"] = traf["id_municipio"].astype(int)

    cont = (
        traf.groupby(["id_municipio", "ano"])
        .size()
        .reset_index(name="n_trafico_drogas")
    )

    munis = cw[["id_municipio"]].drop_duplicates()
    grid = (
        munis.assign(key=1)
        .merge(pd.DataFrame({"ano": ANOS, "key": 1}), on="key")
        .drop(columns="key")
    )
    return grid.merge(cont, on=["id_municipio", "ano"], how="left").assign(
        n_trafico_drogas=lambda d: d["n_trafico_drogas"].fillna(0).astype(int)
    )


def main() -> None:
    if not os.path.isfile(TRAFICO_PATH):
        raise FileNotFoundError(
            f"Base de tráfico não encontrada: {TRAFICO_PATH}. "
            "Execute build_trafico_drogas_ssp.py antes."
        )
    if not os.path.isfile(PAINEL_PATH):
        raise FileNotFoundError(
            f"Painel não encontrado: {PAINEL_PATH}. Execute build_painel.py antes."
        )

    cont = carregar_contagens()
    painel = pd.read_csv(PAINEL_PATH)

    for col in ("taxa_trafico_drogas_100k",):
        if col in painel.columns:
            painel = painel.drop(columns=[col])

    painel = painel.merge(cont[["id_municipio", "ano", "n_trafico_drogas"]], on=["id_municipio", "ano"], how="left")
    painel["n_trafico_drogas"] = painel["n_trafico_drogas"].fillna(0).astype(int)
    painel["taxa_trafico_drogas_100k"] = (
        painel["n_trafico_drogas"] / painel["populacao"] * 100_000
    )
    painel = painel.drop(columns=["n_trafico_drogas"])

    cols = [c for c in painel.columns if c != "taxa_trafico_drogas_100k"]
    cols.append("taxa_trafico_drogas_100k")
    painel = painel[cols].sort_values(["id_municipio", "ano"]).reset_index(drop=True)

    painel.to_csv(PAINEL_PATH, index=False, encoding="utf-8-sig")

    print(f"Salvo: {PAINEL_PATH}")
    print(f"Dimensão: {painel.shape}")
    print("\nResumo taxa_trafico_drogas_100k:")
    print(painel["taxa_trafico_drogas_100k"].describe())


if __name__ == "__main__":
    main()
