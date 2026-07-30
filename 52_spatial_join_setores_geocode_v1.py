# ============================================================
# 52_spatial_join_setores_geocode_v1.py
#
# Recuperação de CD_SETOR por coordenadas geocodificadas
#
# geocode
#    ↓
# pontos
#    ↓
# spatial join IBGE
#    ↓
# CD_SETOR
#
# ============================================================


import os
import time
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


print("="*70)
print("SPATIAL JOIN - GEOCODE x SETORES IBGE")
print("="*70)


inicio = time.time()


# ------------------------------------------------------------
# arquivos
# ------------------------------------------------------------

ENTRADA_GEOCODE = (
    "resultados/enderecos_geocodificados.csv"
)


SHAPE_SETOR = (
    "joinville_setores_mapa.shp"
)


SAIDA = (
    "resultados/enderecos_com_setor_spatial_join.csv"
)


RESUMO = (
    "resultados/resumo_spatial_join.csv"
)



# ------------------------------------------------------------
# leitura
# ------------------------------------------------------------

print("\nLendo geocodificação...")


df = pd.read_csv(
    ENTRADA_GEOCODE,
    low_memory=False
)


print(
    "Endereços:",
    len(df)
)



# ------------------------------------------------------------
# corrigir coordenadas
# ------------------------------------------------------------

df["latitude"] = pd.to_numeric(
    df["latitude"],
    errors="coerce"
)


df["longitude"] = pd.to_numeric(
    df["longitude"],
    errors="coerce"
)


pontos = df[
    df["latitude"].notna()
    &
    df["longitude"].notna()
].copy()


print(
    "Com coordenadas:",
    len(pontos)
)



# ------------------------------------------------------------
# criar pontos
# ------------------------------------------------------------

gdf = gpd.GeoDataFrame(

    pontos,

    geometry=[

        Point(x,y)

        for x,y in zip(

            pontos["longitude"],

            pontos["latitude"]

        )

    ],

    crs="EPSG:4326"

)



# ------------------------------------------------------------
# ler setores
# ------------------------------------------------------------

print("\nLendo setores IBGE...")


setores = gpd.read_file(
    SHAPE_SETOR
)


print(
    "Setores encontrados:",
    len(setores)
)



print(
    "\nColunas disponíveis:"
)

print(
    setores.columns.tolist()
)



# ------------------------------------------------------------
# garantir CRS
# ------------------------------------------------------------

if setores.crs != gdf.crs:

    setores = setores.to_crs(
        gdf.crs
    )



# ------------------------------------------------------------
# spatial join
# ------------------------------------------------------------

print("\nExecutando spatial join...")


resultado = gpd.sjoin(

    gdf,

    setores[

        [

            "CD_SETOR",

            "geometry"

        ]

    ],

    how="left",

    predicate="within"

)



# ------------------------------------------------------------
# classificação
# ------------------------------------------------------------

resultado["metodo_atribuicao"] = (
    "GEOCODE_SPATIAL_JOIN"
)


resultado["confianca"] = "SEM_SETOR"


resultado.loc[

    resultado["CD_SETOR"].notna(),

    "confianca"

] = "ALTA"



# ------------------------------------------------------------
# remover geometria
# ------------------------------------------------------------

resultado = resultado.drop(

    columns=[

        "geometry",

        "index_right"

    ],

    errors="ignore"

)



# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

resultado.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)



# ------------------------------------------------------------
# resumo
# ------------------------------------------------------------

total = len(resultado)


com_setor = (

    resultado["CD_SETOR"]

    .notna()

    .sum()

)


sem_setor = (

    resultado["CD_SETOR"]

    .isna()

    .sum()

)


percentual = (

    com_setor

    /

    total

    *

    100

)


resumo = pd.DataFrame(

    {

        "indicador":[

            "enderecos_processados",

            "com_CD_SETOR",

            "sem_CD_SETOR",

            "percentual_cobertura"

        ],

        "valor":[

            total,

            com_setor,

            sem_setor,

            round(percentual,2)

        ]

    }

)


resumo.to_csv(

    RESUMO,

    index=False,

    encoding="utf-8-sig"

)



print("\n")
print("="*70)
print("RESULTADO")
print("="*70)


print(resumo)


print("\nArquivos gerados:")

print(SAIDA)

print(RESUMO)



tempo = round(

    time.time()-inicio,

    2

)


print("\nTempo:")

print(

    tempo,

    "segundos"

)


print("\nFim.")