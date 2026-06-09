"""
Chaves de texto para cruzar nomes de município da SSP (NOME_MUNICIPIO)
com nomes oficiais da base de população (IBGE / tabela local).

As duas pontas (nome oficial e NOME_MUNICIPIO dos BOs) passam pela MESMA
normalização `_chave`, robusta às divergências de grafia da SSP:

  - abreviações de santo/santa/são: "S.JOSE DO RIO PARDO" == "São José do Rio Pardo";
  - conectivos ("do/da/de/dos/das/d"): "MIRANTE PARANAPANEMA" == "Mirante do Paranapanema";
  - apóstrofo d'Oeste: "ESTRELA D OESTE" == "Estrela d'Oeste";
  - abreviações de cauda: "EUCLIDES DA CUNHA PTA" == "Euclides da Cunha Paulista";
  - variante de grafia "LUIZ"/"LUIS": "S.LUIZ DO PARAITINGA" == "São Luís do Paraitinga".

Validação (commit de referência): cruza 100% dos BOs de feminicídio e de tráfico
de SP; só não casam registros genuinamente de fora do estado (Poços de Caldas/MG,
Monte Santo de Minas/MG, "Outro País"). Os 645 municípios oficiais geram 645
chaves distintas (sem colisão).
"""

from __future__ import annotations

import unicodedata

# Tokens descartados: variantes de santo/santa/são (inclui "S" solto das
# abreviações da SSP) e conectivos. Como os 645 nomes oficiais permanecem
# únicos após o descarte, remover esses tokens não gera ambiguidade.
_DESCARTAR = {
    "SAO", "SANTO", "SANTA", "STO", "STA", "S",
    "DO", "DA", "DE", "DOS", "DAS", "D",
}

# Substituições token-a-token (abreviações de cauda / grafia da SSP).
_SUBSTITUIR = {
    "PTA": "PAULISTA",
    "LUIZ": "LUIS",
}


def _chave(nome: str) -> str:
    """Normalização canônica compartilhada pelas duas pontas do cruzamento."""
    s = (
        unicodedata.normalize("NFKD", str(nome).strip())
        .encode("ascii", "ignore")
        .decode("ascii")
        .upper()
    )
    for ch in ("'", "`", ".", "-", "/"):
        s = s.replace(ch, " ")
    toks = [_SUBSTITUIR.get(t, t) for t in s.split()]
    toks = [t for t in toks if t not in _DESCARTAR]
    return " ".join(toks)


def chave_municipio_oficial(nome: str) -> str:
    """Chave canônica a partir do nome oficial (coluna `municipio` da base de população)."""
    return _chave(nome)


def chave_nome_bo(nome_bo: str) -> str:
    """Chave canônica a partir de `NOME_MUNICIPIO` nos BOs da SSP."""
    return _chave(nome_bo)
