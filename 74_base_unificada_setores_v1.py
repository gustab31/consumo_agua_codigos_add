# ============================================================
# 74_base_unificada_setores_v1.py
#
# BASE MESTRE DOS SETORES CENSITÁRIOS
#
# Objetivo:
#
# Consolidar automaticamente:
#
# - Shapefile dos setores censitários
# - Base IBGE
# - Consumo (CSV 1)
# - Consumo (CSV 2)
# - Relatório 75
# - TXT
#
# Gerando uma única base por CD_SETOR
#
# ============================================================

import os
import glob
import time
import warnings

import numpy as np
import pandas as pd
import geopandas as gpd

warnings.filterwarnings("ignore")

inicio = time.time()

print("="*70)
print("BASE UNIFICADA DOS SETORES CENSITÁRIOS")
print("="*70)


# ============================================================
# PASTAS
# ============================================================

PASTA = "."

RESULTADOS = "resultados"

os.makedirs(
    RESULTADOS,
    exist_ok=True
)


# ============================================================
# FUNÇÃO AUXILIAR
# ============================================================

def localizar_arquivo(padroes):

    for padrao in padroes:

        arquivos = glob.glob(
            os.path.join(
                PASTA,
                padrao
            )
        )

        if len(arquivos):

            print(f"OK  {arquivos[0]}")

            return arquivos[0]

    return None


# ============================================================
# LOCALIZAR SHAPEFILE
# ============================================================

print("\nLocalizando shapefile...")

# prioridade absoluta para a malha dos setores

padroes = [

    "*joinville_setores_mapa.shp",

    "*Joinville_setores_mapa.shp",

    "*setores_mapa.shp",

    "*malha*.shp",

    "*setores*.shp"

]

arquivo_shp = None

for p in padroes:

    arqs = glob.glob(os.path.join(PASTA, p))

    if arqs:

        arquivo_shp = arqs[0]
        break

if arquivo_shp is None:

    raise FileNotFoundError(
        "Não foi encontrado o shapefile da malha censitária."
    )

print("Arquivo utilizado:")
print(arquivo_shp)

if arquivo_shp is None:

    raise FileNotFoundError(

        "Shapefile não encontrado."

    )


# ============================================================
# LOCALIZAR IBGE
# ============================================================

print("\nLocalizando base IBGE...")

arquivo_ibge = localizar_arquivo([

    "*Agregados*.xlsx",

    "*renda*.xlsx",

    "*IBGE*.xlsx"

])

if arquivo_ibge is None:

    raise FileNotFoundError(

        "Planilha IBGE não encontrada."

    )


# ============================================================
# LOCALIZAR CSV
# ============================================================

print("\nLocalizando bases de consumo...")

csvs = sorted(

    glob.glob(

        os.path.join(

            PASTA,

            "*.csv"

        )

    )

)

csvs = [

    c for c in csvs

    if "resultado" not in c.lower()

]

print(

    "CSV encontrados:",

    len(csvs)

)

for c in csvs:

    print(

        "   ", os.path.basename(c)

    )


# ============================================================
# LOCALIZAR RELATÓRIO 75
# ============================================================

print("\nLocalizando Relatório 75...")

arquivo_relatorio = localizar_arquivo([

    "*75*.xlsx",

    "*relatorio*.xlsx"

])


# ============================================================
# LOCALIZAR TXT
# ============================================================

print("\nLocalizando TXT...")

txts = glob.glob(

    "*.txt"

)

arquivo_txt = None

if len(txts):

    arquivo_txt = txts[0]

    print(

        "OK",

        arquivo_txt

    )


# ============================================================
# LER SHAPEFILE
# ============================================================

print("\nLendo shapefile...")

gdf = gpd.read_file(

    arquivo_shp

)

print(

    "Registros:",

    len(gdf)

)

print(

    "Colunas:",

    len(gdf.columns)

)

print(

    "CRS:",

    gdf.crs

)

print("\nColunas:")

for c in gdf.columns:

    print(" -", c)


# ============================================================
# DETECTAR CD_SETOR
# ============================================================

print("\nProcurando coluna do setor...")

coluna_setor = None

for c in gdf.columns:

    nome = c.upper()

    if "SETOR" in nome:

        coluna_setor = c

        break

    if "CD_GEOCODI" in nome:

        coluna_setor = c

        break

    if "CD_SETOR" in nome:

        coluna_setor = c

        break

if coluna_setor is None:

    raise Exception(

        "Não foi possível identificar a coluna do setor."

    )

print(

    "Coluna utilizada:",

    coluna_setor

)

gdf[coluna_setor] = (

    gdf[coluna_setor]

    .astype(str)

)

print(

    "\nSetores únicos:",

    gdf[coluna_setor].nunique()

)