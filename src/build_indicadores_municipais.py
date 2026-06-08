"""
build_indicadores_municipais.py
================================
Constrói `processed/indicadores_municipais.csv`: um indicador por município
(nível município, invariante no tempo — referência Censo 2022 / PIB 2022-2023).

Fontes (raw/socioeconomicos/):
  - alfabetizacao.csv       -> SIDRA 9542 (Censo 2022): pessoas 15+ alfabetizadas
  - anos_estudos.csv        -> SIDRA 10062 (Censo 2022): anos médios de estudo 11+
  - nivel-escolaridade.csv  -> SIDRA 10061 (Censo 2022): pessoas 18+ por nível de instrução
  - pib_municipal.csv       -> PIB municipal a preços correntes (2002-2023)

Indicadores produzidos (1 por município, recorte total):
  pib_per_capita_2022, taxa_alfabetizacao, anos_medios_estudo,
  pct_ensino_medio    (% 18+ com médio completo ou mais),
  pct_ensino_superior (% 18+ com superior completo).
Descartados por redundância: recortes femininos (r≈0,97 com o total) e pib_2023
(r≈0,9998 com pib_2022). Recorte por raça: ausente nos CSVs baixados (não extraído).

Chave de merge: id_municipio (código IBGE de 7 dígitos).
  - PIB já traz Cod_mun = id_municipio.
  - alfabetizacao / anos_estudos trazem só o nome ("Município (SP)") -> casamos
    por chave textual canônica contra o crosswalk derivado da base de população.

Uso: python src/build_indicadores_municipais.py
"""
from __future__ import annotations

import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from municipio_sp import chave_municipio_oficial  # noqa: E402

RAW_SOCIO = os.path.join(ROOT, "raw", "socioeconomicos")
RAW_IBGE = os.path.join(ROOT, "raw", "ibge")
PROCESSED = os.path.join(ROOT, "processed")

# Aliases nome->chave para municípios cuja grafia no SIDRA difere da base de população.
ALIASES_SIDRA: dict[str, str] = {
    "MOJI MIRIM": "MOGI MIRIM",
    "SAO LUIZ DO PARAITINGA": "SAO LUIS DO PARAITINGA",
    "FLORINEA": "FLORINIA",
    "EMBU": "EMBU DAS ARTES",
}


def _chave(nome: str) -> str:
    nome = str(nome).replace("(SP)", "").strip()
    k = chave_municipio_oficial(nome)
    return ALIASES_SIDRA.get(k, k)


def carregar_crosswalk() -> pd.DataFrame:
    """id_municipio + chave canônica a partir da base de população do IBGE."""
    pop = pd.read_csv(os.path.join(RAW_IBGE, "populacao_municipio_SP.csv"))
    cw = (
        pop[["id_municipio", "municipio"]]
        .drop_duplicates()
        .assign(chave=lambda d: d["municipio"].map(chave_municipio_oficial))
    )
    return cw


# ---------------------------------------------------------------------------
# PIB
# ---------------------------------------------------------------------------
def carregar_pib() -> pd.DataFrame:
    pib = pd.read_csv(
        os.path.join(RAW_SOCIO, "pib_municipal.csv"), sep=";", encoding="utf-8-sig"
    )
    pib.columns = [c.strip() for c in pib.columns]

    def _parse_reais(v: str) -> float:
        s = str(v).replace("R$", "").replace(" ", "").replace(".", "")
        s = s.rstrip(",").replace(",", ".")
        return float(s) if s not in ("", "nan") else float("nan")

    pib["pib_reais"] = pib["PIB"].map(_parse_reais)
    pib = pib.rename(columns={"Cod_mun": "id_municipio", "Ano": "ano"})
    # Mantemos só 2022 (alinhado ao Censo 2022). pib_2023 descartado:
    # correlação pib_2022~pib_2023 ≈ 0,9998 (redundante).
    pib_wide = (
        pib[pib["ano"] == 2022]
        .pivot_table(index="id_municipio", columns="ano", values="pib_reais")
        .rename(columns={2022: "pib_2022"})
        .reset_index()
    )
    pib_wide.columns.name = None
    return pib_wide


# ---------------------------------------------------------------------------
# Alfabetização (SIDRA 9542, Censo 2022) — tabela de valores absolutos
# ---------------------------------------------------------------------------
def carregar_alfabetizacao(cw: pd.DataFrame) -> pd.DataFrame:
    raw = pd.read_csv(
        os.path.join(RAW_SOCIO, "alfabetizacao.csv"),
        sep=";",
        header=None,
        names=list(range(12)),
        engine="python",
        on_bad_lines="skip",
        encoding="utf-8-sig",
        dtype=str,
    )
    # Linhas de município = col0 termina em "(SP)". O arquivo traz DUAS tabelas
    # (absolutos e %); ficamos com a 1ª ocorrência de cada município (absolutos).
    mun = raw[raw[0].astype(str).str.endswith("(SP)")].copy()
    mun = mun.drop_duplicates(subset=[0], keep="first")

    def num(col):
        return pd.to_numeric(mun[col].str.replace(".", "", regex=False), errors="coerce")

    out = pd.DataFrame({"municipio_raw": mun[0]})
    out["pop15_total"] = num(3)
    out["alfab_total"] = num(6)
    out["chave"] = out["municipio_raw"].map(_chave)
    out["taxa_alfabetizacao"] = out["alfab_total"] / out["pop15_total"]

    merged = out.merge(cw, on="chave", how="left")
    faltam = merged[merged["id_municipio"].isna()]["municipio_raw"].tolist()
    if faltam:
        print(f"[alfabetizacao] {len(faltam)} sem match:", faltam)
    return merged.dropna(subset=["id_municipio"])[
        ["id_municipio", "taxa_alfabetizacao"]
    ]


# ---------------------------------------------------------------------------
# Anos de estudo (SIDRA 10062, Censo 2022) — média de anos, pessoas 11+
# ---------------------------------------------------------------------------
def carregar_anos_estudo(cw: pd.DataFrame) -> pd.DataFrame:
    raw = pd.read_csv(
        os.path.join(RAW_SOCIO, "anos_estudos.csv"),
        sep=";",
        header=None,
        names=list(range(8)),
        engine="python",
        on_bad_lines="skip",
        encoding="utf-8-sig",
        dtype=str,
    )
    mun = raw[raw[0].astype(str).str.endswith("(SP)")].copy()
    mun = mun.drop_duplicates(subset=[0], keep="first")

    def dec(col):
        return pd.to_numeric(mun[col].str.replace(",", ".", regex=False), errors="coerce")

    out = pd.DataFrame({"municipio_raw": mun[0]})
    out["anos_medios_estudo"] = dec(2)       # 11+ total
    out["chave"] = out["municipio_raw"].map(_chave)

    merged = out.merge(cw, on="chave", how="left")
    faltam = merged[merged["id_municipio"].isna()]["municipio_raw"].tolist()
    if faltam:
        print(f"[anos_estudos] {len(faltam)} sem match:", faltam)
    return merged.dropna(subset=["id_municipio"])[
        ["id_municipio", "anos_medios_estudo"]
    ]


# ---------------------------------------------------------------------------
# Nível de instrução (SIDRA 10061, Censo 2022) — pessoas 18+ por nível
# ---------------------------------------------------------------------------
def carregar_nivel_escolaridade(cw: pd.DataFrame) -> pd.DataFrame:
    """% da população 18+ com ensino médio completo (ou mais) e com superior completo.

    O arquivo traz DUAS tabelas (absolutos e %) e três linhas de sexo por município
    (Total/Homens/Mulheres). Ficamos com a 1ª ocorrência de cada município no recorte
    Sexo='Total' (= tabela de absolutos) e calculamos os percentuais nós mesmos.
    Separador é VÍRGULA (diferente das outras bases, que usam ';').
    """
    raw = pd.read_csv(
        os.path.join(RAW_SOCIO, "nivel-escolaridade.csv"),
        sep=",",
        header=None,
        names=list(range(8)),
        engine="python",
        on_bad_lines="skip",
        encoding="utf-8-sig",
        dtype=str,
    )
    # Colunas: 0=Município 1=Sexo 2=Cor/raça 3=Total(18+)
    #   4=Sem instr.+fund. incompleto   5=Fund. completo+médio incompleto
    #   6=Médio completo+superior incompleto   7=Superior completo
    mun = raw[raw[0].astype(str).str.endswith("(SP)")]
    tot = mun[mun[1] == "Total"].drop_duplicates(subset=[0], keep="first").copy()

    def num(col):
        return pd.to_numeric(tot[col], errors="coerce")

    pop18 = num(3)
    out = pd.DataFrame({"municipio_raw": tot[0]})
    out["pct_ensino_medio"] = (num(6) + num(7)) / pop18      # médio completo OU mais
    out["pct_ensino_superior"] = num(7) / pop18              # superior completo
    out["chave"] = out["municipio_raw"].map(_chave)

    merged = out.merge(cw, on="chave", how="left")
    faltam = merged[merged["id_municipio"].isna()]["municipio_raw"].tolist()
    if faltam:
        print(f"[nivel-escolaridade] {len(faltam)} sem match:", faltam)
    return merged.dropna(subset=["id_municipio"])[
        ["id_municipio", "pct_ensino_medio", "pct_ensino_superior"]
    ]


def main() -> None:
    cw = carregar_crosswalk()
    base = cw[["id_municipio", "municipio"]].drop_duplicates().copy()

    pop22 = (
        pd.read_csv(os.path.join(RAW_IBGE, "populacao_municipio_SP.csv"))
        .query("ano == 2022")[["id_municipio", "populacao"]]
        .rename(columns={"populacao": "populacao_2022"})
    )

    pib = carregar_pib()
    alfab = carregar_alfabetizacao(cw)
    anos = carregar_anos_estudo(cw)
    nivel = carregar_nivel_escolaridade(cw)

    ind = (
        base.merge(pop22, on="id_municipio", how="left")
        .merge(pib, on="id_municipio", how="left")
        .merge(alfab, on="id_municipio", how="left")
        .merge(anos, on="id_municipio", how="left")
        .merge(nivel, on="id_municipio", how="left")
    )
    ind["pib_per_capita_2022"] = ind["pib_2022"] / ind["populacao_2022"]

    cols = [
        "id_municipio",
        "municipio",
        "populacao_2022",
        "pib_2022",
        "pib_per_capita_2022",
        "taxa_alfabetizacao",
        "anos_medios_estudo",
        "pct_ensino_medio",
        "pct_ensino_superior",
    ]
    ind = ind[cols].sort_values("id_municipio").reset_index(drop=True)

    os.makedirs(PROCESSED, exist_ok=True)
    saida = os.path.join(PROCESSED, "indicadores_municipais.csv")
    ind.to_csv(saida, index=False, encoding="utf-8-sig")

    print(f"\nSalvo: {saida}")
    print(f"Municípios: {len(ind)}")
    print("Cobertura (não-nulos) por coluna:")
    print(ind.notna().sum())


if __name__ == "__main__":
    main()
