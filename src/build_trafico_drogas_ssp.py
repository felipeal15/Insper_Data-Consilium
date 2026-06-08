"""
build_trafico_drogas_ssp.py
===========================
Constrói `raw/ssp/trafico_drogas_2022_2025.csv` a partir dos BOs brutos em `csv/`.

Replica a lógica de `limpeza.ipynb` / `padronizar_colunas.py`:
  - concatena os 8 arquivos semestrais (2022–2025);
  - padroniza nomes de colunas;
  - mantém apenas colunas completas em todos os anos;
  - filtra BOs de tráfico de drogas (Art. 33, caput — RUBRICA);
  - descarta registros inválidos (município/ano ausentes ou fora de 2022–2025).

Uso: python src/build_trafico_drogas_ssp.py
"""
from __future__ import annotations

import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from padronizar_colunas import (  # noqa: E402
    COMPLETE_COLUMNS,
    carregar_e_padronizar,
    filtrar_colunas_completas,
)

CSV_DIR = os.path.join(ROOT, "csv")
RAW_SSP = os.path.join(ROOT, "raw", "ssp")
ANOS = [2022, 2023, 2024, 2025]

ARQUIVOS_SEMESTRAIS = [
    "2022_JAN_JUN.csv",
    "2022_JUL_DEZ.csv",
    "2023_JAN_JUN.csv",
    "2023_JUL_DEZ.csv",
    "2024_JAN_JUN.csv",
    "2024_JUL_DEZ.csv",
    "2025_JAN_JUN.csv",
    "2025_JUL_DEZ.csv",
]

SAIDA = os.path.join(RAW_SSP, "trafico_drogas_2022_2025.csv")


def eh_trafico_drogas(rubrica: str) -> bool:
    """Identifica BOs de tráfico (Art. 33, caput), excluindo consumo pessoal (Art. 28)."""
    r = str(rubrica or "").strip().lower()
    if not r or r == "null":
        return False
    if "art.28" in r:
        return False
    if "tráfico drogas" in r or "trafico drogas" in r:
        return True
    return "art.33" in r and "caput" in r


def carregar_bos_padronizados() -> pd.DataFrame:
    partes = []
    for nome in ARQUIVOS_SEMESTRAIS:
        caminho = os.path.join(CSV_DIR, nome)
        if not os.path.isfile(caminho):
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
        partes.append(carregar_e_padronizar(caminho))

    df = pd.concat(partes, ignore_index=True)
    return filtrar_colunas_completas(df)


def filtrar_trafico_valido(df: pd.DataFrame) -> pd.DataFrame:
    traf = df[df["RUBRICA"].map(eh_trafico_drogas)].copy()

    traf = traf.dropna(subset=["NOME_MUNICIPIO", "ANO_ESTATISTICA"])
    traf["NOME_MUNICIPIO"] = traf["NOME_MUNICIPIO"].astype(str).str.strip()
    traf = traf[traf["NOME_MUNICIPIO"].ne("")]

    traf["ANO_ESTATISTICA"] = pd.to_numeric(traf["ANO_ESTATISTICA"], errors="coerce")
    traf = traf.dropna(subset=["ANO_ESTATISTICA"])
    traf["ANO_ESTATISTICA"] = traf["ANO_ESTATISTICA"].astype(int)
    traf = traf[traf["ANO_ESTATISTICA"].isin(ANOS)]

    cols = [c for c in COMPLETE_COLUMNS if c in traf.columns]
    return traf[cols].sort_values(
        ["ANO_ESTATISTICA", "NOME_MUNICIPIO", "NUM_BO"]
    ).reset_index(drop=True)


def main() -> None:
    print("Carregando e padronizando BOs brutos...")
    df = carregar_bos_padronizados()
    print(f"  Total de BOs (todas as rubricas): {len(df):,}")

    traf = filtrar_trafico_valido(df)
    os.makedirs(RAW_SSP, exist_ok=True)
    traf.to_csv(SAIDA, index=False, encoding="utf-8-sig")

    print(f"\nSalvo: {SAIDA}")
    print(f"BOs de tráfico de drogas: {len(traf):,}")
    print("Contagem por ano:")
    print(traf.groupby("ANO_ESTATISTICA").size())
    print(f"Municípios distintos: {traf['NOME_MUNICIPIO'].nunique()}")


if __name__ == "__main__":
    main()
