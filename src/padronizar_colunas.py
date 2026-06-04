"""
Script para padronizar colunas de bases de dados (2022-2025)
Solução para: nomes inconsistentes, colunas faltando, problema de acentuação
"""

import pandas as pd

# Mapeamento de renomeações para padronização
RENAME_MAPPING = {
    # Período
    "DESCR_PERIODO": "DESC_PERIODO",
    
    # Município
    "CIDADE": "NOME_MUNICIPIO",
    
    # Acentuação (remover circunflexo para padronizar)
    "NOME_DELEGACIA_CIRCUNSCRIÇÃO": "NOME_DELEGACIA_CIRCUNSCRICAO",
    "NOME_DEPARTAMENTO_CIRCUNSCRIÇÃO": "NOME_DEPARTAMENTO_CIRCUNSCRICAO",
    "NOME_MUNICIPIO_CIRCUNSCRIÇÃO": "NOME_MUNICIPIO_CIRCUNSCRICAO",
    "NOME_SECCIONAL_CIRCUNSCRIÇÃO": "NOME_SECCIONAL_CIRCUNSCRICAO",
}

# Colunas que existem em TODOS os 4 anos (após padronização)
COMPLETE_COLUMNS = [
    'ANO_BO',
    'ANO_ESTATISTICA',
    'BAIRRO',
    'DATA_OCORRENCIA_BO',
    'DESCR_CONDUTA',
    'DESC_PERIODO',
    'HORA_OCORRENCIA_BO',
    'LATITUDE',
    'LOGRADOURO',
    'LONGITUDE',
    'MES_ESTATISTICA',
    'NATUREZA_APURADA',
    'NOME_DELEGACIA',
    'NOME_DELEGACIA_CIRCUNSCRICAO',
    'NOME_DEPARTAMENTO',
    'NOME_DEPARTAMENTO_CIRCUNSCRICAO',
    'NOME_MUNICIPIO',
    'NOME_MUNICIPIO_CIRCUNSCRICAO',
    'NOME_SECCIONAL',
    'NOME_SECCIONAL_CIRCUNSCRICAO',
    'NUMERO_LOGRADOURO',
    'NUM_BO',
    'RUBRICA',
]

def padronizar_df(df):
    """
    Padroniza nomes de colunas de um dataframe.
    
    Parâmetros:
        df (pd.DataFrame): Dataframe para padronizar
    
    Retorna:
        pd.DataFrame: Dataframe com nomes padronizados
    """
    return df.rename(columns=RENAME_MAPPING)

def carregar_e_padronizar(caminho_csv, sep=";", encoding="utf-8-sig"):
    """
    Carrega um CSV e padroniza seus nomes de colunas.
    
    Parâmetros:
        caminho_csv (str): Caminho para o arquivo CSV
        sep (str): Separador do CSV (padrão: ";")
        encoding (str): Encoding do arquivo (padrão: "utf-8-sig")
    
    Retorna:
        pd.DataFrame: Dataframe carregado e padronizado
    """
    df = pd.read_csv(caminho_csv, sep=sep, encoding=encoding)
    return padronizar_df(df)

def filtrar_colunas_completas(df):
    """
    Filtra dataframe para manter apenas colunas completas.
    
    Parâmetros:
        df (pd.DataFrame): Dataframe para filtrar
    
    Retorna:
        pd.DataFrame: Dataframe com apenas colunas completas
    """
    # Manter apenas colunas que existem e que são completas
    cols_to_keep = [col for col in COMPLETE_COLUMNS if col in df.columns]
    return df[cols_to_keep]

# Exemplo de uso
if __name__ == "__main__":
    # Carregar bases individuais
    df_2022 = carregar_e_padronizar("Bases/csv/2022_JAN_JUN.csv")
    df_2023 = carregar_e_padronizar("Bases/csv/2023_JAN_JUN.csv")
    df_2024 = carregar_e_padronizar("Bases/csv/2024_JAN_JUN.csv")
    df_2025 = carregar_e_padronizar("Bases/csv/2025_JAN_JUN.csv")
    
    # Concatenar
    df_total = pd.concat([df_2022, df_2023, df_2024, df_2025], ignore_index=True)
    
    # Opção 1: Manter todas as colunas (com NaN onde houver falta)
    print(f"df_total: {df_total.shape[0]} linhas, {df_total.shape[1]} colunas")
    
    # Opção 2: Manter APENAS colunas completas (sem NaN) - RECOMENDADO
    df_total_completo = filtrar_colunas_completas(df_total)
    print(f"df_total_completo: {df_total_completo.shape[0]} linhas, {df_total_completo.shape[1]} colunas")
