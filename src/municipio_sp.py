"""
Chaves de texto para cruzar nomes de município da SSP (NOME_MUNICIPIO)
com nomes oficiais da base de população (IBGE / tabela local).
"""

from __future__ import annotations

import unicodedata


def chave_municipio_oficial(nome: str) -> str:
    """Chave canônica a partir do nome oficial (ex.: coluna municipio do CSV de população)."""
    s = unicodedata.normalize("NFKD", str(nome).strip()).encode("ascii", "ignore").decode("ascii")
    s = s.replace("'", "").replace("`", "")
    s = s.upper().replace("-", " ").replace(".", " ")
    return " ".join(s.split())


def chave_nome_bo(nome_bo: str) -> str:
    """Chave a partir de NOME_MUNICIPIO nos BOs (abreviações S., etc.)."""
    s = unicodedata.normalize("NFKD", str(nome_bo).strip()).encode("ascii", "ignore").decode("ascii")
    s = " ".join(s.upper().replace(".", " ").replace("-", " ").split())
    if s == "S PAULO":
        return "SAO PAULO"
    return FEM_CHAVE_ALIASES.get(s, s)


# norm(BO) -> chave igual à de chave_municipio_oficial(...) na base de população
FEM_CHAVE_ALIASES: dict[str, str] = {
    "ESPIRITO STO PINHAL": "ESPIRITO SANTO DO PINHAL",
    "PIRAPORA BOM JESUS": "PIRAPORA DO BOM JESUS",
    "RIBEIRAO INDIOS": "RIBEIRAO DOS INDIOS",
    "S ALBERTINA": "SANTA ALBERTINA",
    "S ANASTACIO": "SANTO ANASTACIO",
    "S ANDRE": "SANTO ANDRE",
    "S ANTONIO DA ALEGRIA": "SANTO ANTONIO DA ALEGRIA",
    "S ANTONIO DE POSSE": "SANTO ANTONIO DE POSSE",
    "S BARBARA D OESTE": "SANTA BARBARA DOESTE",
    "S BERNARDO DO CAMPO": "SAO BERNARDO DO CAMPO",
    "S BRANCA": "SANTA BRANCA",
    "S CAETANO DO SUL": "SAO CAETANO DO SUL",
    "S CARLOS": "SAO CARLOS",
    "S CRUZ DAS PALMEIRAS": "SANTA CRUZ DAS PALMEIRAS",
    "S CRUZ DO RIO PARDO": "SANTA CRUZ DO RIO PARDO",
    "S ERNESTINA": "SANTA ERNESTINA",
    "S FE DO SUL": "SANTA FE DO SUL",
    "S GERTRUDES": "SANTA GERTRUDES",
    "S ISABEL": "SANTA ISABEL",
    "S JOAO DA BOA VISTA": "SAO JOAO DA BOA VISTA",
    "S JOAO DO PAU D ALHO": "SAO JOAO DO PAU DALHO",
    "S JOAQUIM DA BARRA": "SAO JOAQUIM DA BARRA",
    "S JOSE DO RIO PRETO": "SAO JOSE DO RIO PRETO",
    "S JOSE DOS CAMPOS": "SAO JOSE DOS CAMPOS",
    "S LUCIA": "SANTA LUCIA",
    "S MANUEL": "SAO MANUEL",
    "S MARIA DA SERRA": "SANTA MARIA DA SERRA",
    "S MIGUEL ARCANJO": "SAO MIGUEL ARCANJO",
    "S ROQUE": "SAO ROQUE",
    "S ROSA DE VITERBO": "SANTA ROSA DE VITERBO",
    "S SEBASTIAO": "SAO SEBASTIAO",
    "S VICENTE": "SAO VICENTE",
}
