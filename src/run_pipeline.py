"""
run_pipeline.py
===============
Orquestra a construção das bases derivadas, na ordem correta:

  raw/  ->  processed/  ->  final/

1. build_indicadores_municipais.py  -> processed/indicadores_municipais.csv
2. build_feminicidios_municipio_ano.py -> processed/feminicidios_municipio_ano.csv
3. build_painel.py                   -> final/painel_feminicidio_sp.csv

Pré-requisitos (já versionados em raw/):
  raw/ssp/feminicidios_2022_2025.csv
  raw/ibge/populacao_municipio_SP.csv
  raw/socioeconomicos/{alfabetizacao,anos_estudos,pib_municipal}.csv

Uso: python src/run_pipeline.py
"""
from __future__ import annotations

import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
ETAPAS = [
    "build_indicadores_municipais.py",
    "build_feminicidios_municipio_ano.py",
    "build_painel.py",
]

if __name__ == "__main__":
    for etapa in ETAPAS:
        print("\n" + "=" * 70)
        print(f">>> {etapa}")
        print("=" * 70)
        runpy.run_path(os.path.join(HERE, etapa), run_name="__main__")
    print("\nPipeline concluído. Dataset final: final/painel_feminicidio_sp.csv")
