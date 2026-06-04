"""
build_feminicidios_municipio_ano.py
===================================
Constrói `processed/feminicidios_municipio_ano.csv`: contagem de feminicídios
por município e ano, com o GRID COMPLETO de 645 municípios x 4 anos (2022-2025),
preenchendo com 0 os municípios-ano sem nenhum registro.

Entrada: raw/ssp/feminicidios_2022_2025.csv (casos filtrados por DESCR_CONDUTA).

ATENÇÃO METODOLÓGICA — a base de casos mistura desfechos:
  NATUREZA_APURADA == "HOMICÍDIO DOLOSO"      -> feminicídio CONSUMADO  (~500)
  NATUREZA_APURADA contém "TENTATIVA"          -> TENTATIVA de feminicídio (~1136)
Por isso geramos colunas separadas: `n_total`, `n_consumado`, `n_tentativa`.
A equipe deve decidir explicitamente qual usar como desfecho na modelagem.

Chave de saída: id_municipio (via crosswalk da base de população) + ano.
Uso: python src/build_feminicidios_municipio_ano.py
"""
from __future__ import annotations

import os
import sys
import unicodedata

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from municipio_sp import chave_municipio_oficial, chave_nome_bo  # noqa: E402

RAW_SSP = os.path.join(ROOT, "raw", "ssp")
RAW_IBGE = os.path.join(ROOT, "raw", "ibge")
PROCESSED = os.path.join(ROOT, "processed")
ANOS = [2022, 2023, 2024, 2025]


def _strip_accents(s: str) -> str:
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode("ascii")


def classificar_desfecho(natureza: str) -> str:
    n = _strip_accents(natureza).upper()
    if "TENTATIVA" in n:
        return "tentativa"
    if "HOMICIDIO DOLOSO" in n:
        return "consumado"
    return "outro"


def main() -> None:
    pop = pd.read_csv(os.path.join(RAW_IBGE, "populacao_municipio_SP.csv"))
    pop = pop[pop["ano"].isin(ANOS)].copy()
    cw = (
        pop[["id_municipio", "municipio"]]
        .drop_duplicates()
        .assign(chave=lambda d: d["municipio"].map(chave_municipio_oficial))
    )

    fem = pd.read_csv(os.path.join(RAW_SSP, "feminicidios_2022_2025.csv"), encoding="utf-8-sig")
    fem = fem.dropna(subset=["NOME_MUNICIPIO", "ANO_ESTATISTICA"]).copy()
    fem["ano"] = fem["ANO_ESTATISTICA"].astype(int)
    fem["chave"] = fem["NOME_MUNICIPIO"].astype(str).str.strip().map(chave_nome_bo)
    fem["desfecho"] = fem["NATUREZA_APURADA"].map(classificar_desfecho)

    # Casa cada caso ao id_municipio via chave textual.
    fem = fem.merge(cw[["id_municipio", "chave"]], on="chave", how="left")
    sem_id = fem["id_municipio"].isna().sum()
    if sem_id:
        print(f"[aviso] {sem_id} casos sem id_municipio (chaves):",
              sorted(fem.loc[fem["id_municipio"].isna(), "chave"].unique())[:20])
    fem = fem.dropna(subset=["id_municipio"])
    fem["id_municipio"] = fem["id_municipio"].astype(int)

    # Contagens por município-ano e desfecho.
    cont = (
        fem.groupby(["id_municipio", "ano", "desfecho"]).size().unstack("desfecho", fill_value=0)
    )
    for col in ["consumado", "tentativa", "outro"]:
        if col not in cont.columns:
            cont[col] = 0
    cont["n_total"] = cont[["consumado", "tentativa", "outro"]].sum(axis=1)
    cont = cont.rename(columns={"consumado": "n_consumado", "tentativa": "n_tentativa",
                                "outro": "n_outro"}).reset_index()

    # Grid completo 645 x 4 anos -> preenche zeros.
    munis = cw[["id_municipio", "municipio"]].drop_duplicates()
    grid = (
        munis.assign(key=1)
        .merge(pd.DataFrame({"ano": ANOS, "key": 1}), on="key")
        .drop(columns="key")
    )
    out = grid.merge(cont, on=["id_municipio", "ano"], how="left")
    for c in ["n_consumado", "n_tentativa", "n_outro", "n_total"]:
        out[c] = out[c].fillna(0).astype(int)

    out = out.sort_values(["id_municipio", "ano"]).reset_index(drop=True)
    os.makedirs(PROCESSED, exist_ok=True)
    saida = os.path.join(PROCESSED, "feminicidios_municipio_ano.csv")
    out.to_csv(saida, index=False, encoding="utf-8-sig")

    print(f"Salvo: {saida}")
    print(f"Linhas (645 x 4): {len(out)}")
    print("Totais por ano:")
    print(out.groupby("ano")[["n_consumado", "n_tentativa", "n_total"]].sum())
    print(f"Municípios-ano com >=1 caso total: {(out['n_total'] > 0).sum()} de {len(out)}")
    print(f"Soma n_total: {out['n_total'].sum()} | consumados: {out['n_consumado'].sum()}")


if __name__ == "__main__":
    main()
