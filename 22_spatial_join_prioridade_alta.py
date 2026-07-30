# ============================================================
# 22_spatial_join_prioridade_alta_v9.py
#
# Geocodificacao prioridade alta
# Spatial Join -> Setor censitario
#
# ============================================================


import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os
import time


inicio = time.time()


print("="*60)
print("SPATIAL JOIN PRIORIDADE ALTA - V9")
print("="*60)



# ============================================================
# ARQUIVOS
# ============================================================


ARQ_GEOCODE = (
    "resultados/"
    "geocode_prioridade_alta_resultado.csv"
)


ARQ_SETOR = (
    "joinville_setores_mapa.shp"
)


SAIDA = (
    "resultados/"
    "resultado_spatial_prioridade_alta_v9.csv"
)


RESUMO = (
    "resultados/"
    "resumo_recuperacao_prioridade_alta_v9.csv"
)



for arq in [

    ARQ_GEOCODE,
    ARQ_SETOR

]:

    if not os.path.exists(arq):

        raise FileNotFoundError(
            arq
        )



# ============================================================
# GEOCODE
# ============================================================


print("\nLendo geocodificação...")


geo = pd.read_csv(

    ARQ_GEOCODE,

    low_memory=False

)



print(
    "Registros:",
    len(geo)
)



geo = geo[

    geo["status_geocode"]
    ==
    "encontrado"

].copy()



print(
    "Encontrados:",
    len(geo)
)



geo["latitude"] = pd.to_numeric(

    geo["latitude"],

    errors="coerce"

)


geo["longitude"] = pd.to_numeric(

    geo["longitude"],

    errors="coerce"

)



geo = geo.dropna(

    subset=[

        "latitude",

        "longitude"

    ]

)



# ============================================================
# PONTOS
# ============================================================


print("\nCriando pontos...")


pontos = gpd.GeoDataFrame(

    geo,

    geometry=[

        Point(x,y)

        for x,y in zip(

            geo["longitude"],

            geo["latitude"]

        )

    ],

    crs="EPSG:4326"

)



print(
    "Pontos:",
    len(pontos)
)



# ============================================================
# SETORES
# ============================================================


print("\nLendo setores...")


setores = gpd.read_file(

    ARQ_SETOR

)



print(
    "Setores:",
    len(setores)
)



print(
    "Colunas:",
    setores.columns.tolist()
)



# garantir geometria


geom_nome = setores.geometry.name


geom = setores.geometry.copy()



# limpar nomes sem destruir geometry


novas_colunas = []


for c in setores.columns:


    if c == geom_nome:

        novas_colunas.append(
            "geometry"
        )

    else:

        novas_colunas.append(

            str(c)
            .strip()
            .upper()

        )



setores.columns = novas_colunas



setores = gpd.GeoDataFrame(

    setores,

    geometry=geom,

    crs=setores.crs

)



# ============================================================
# CD_SETOR
# ============================================================


if "CD_SETOR" not in setores.columns:


    candidatos = [

        c for c in setores.columns

        if "SETOR" in c

    ]


    print(
        "Candidatos:",
        candidatos
    )


    if len(candidatos) == 1:

        setores.rename(

            columns={

                candidatos[0]:
                "CD_SETOR"

            },

            inplace=True

        )


    else:

        raise Exception(
            "CD_SETOR não encontrado"
        )



print(
    "CD_SETOR OK"
)



# renomear para evitar conflito


setores.rename(

    columns={

        "CD_SETOR":
        "SETOR_IBGE"

    },

    inplace=True

)



# ============================================================
# CRS
# ============================================================


if setores.crs != pontos.crs:

    setores = setores.to_crs(

        pontos.crs

    )



# ============================================================
# SPATIAL JOIN
# ============================================================


print("\nExecutando spatial join...")


resultado = gpd.sjoin(

    pontos,

    setores[

        [

            "SETOR_IBGE",

            "geometry"

        ]

    ],

    how="left",

    predicate="within"

)



print(
    "Após join:"
)


print(
    resultado.columns.tolist()
)



# ============================================================
# CRIAR CD_SETOR FINAL
# ============================================================


resultado["CD_SETOR"] = resultado["SETOR_IBGE"]



# método


resultado["metodo_setor"] = resultado.apply(

    lambda x:

    "spatial"

    if pd.notna(x["CD_SETOR"])

    else "nao_encontrado",

    axis=1

)



resultado["confianca"] = resultado.apply(

    lambda x:

    "alta"

    if pd.notna(x["CD_SETOR"])

    else "nenhuma",

    axis=1

)



# ============================================================
# GARANTIR MATRICULAS
# ============================================================


if "total_matriculas" not in resultado.columns:

    resultado["total_matriculas"] = 0



resultado["total_matriculas"] = pd.to_numeric(

    resultado["total_matriculas"],

    errors="coerce"

).fillna(0)



# ============================================================
# SALVAR
# ============================================================


resultado.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)



resumo = pd.DataFrame({

    "indicador":[

        "enderecos_geocodificados",

        "enderecos_com_CD_SETOR",

        "matriculas_potenciais"

    ],

    "valor":[

        len(resultado),

        resultado["CD_SETOR"]
        .notna()
        .sum(),

        resultado["total_matriculas"]
        .sum()

    ]

})



resumo.to_csv(

    RESUMO,

    index=False,

    encoding="utf-8-sig"

)



# ============================================================
# FINAL
# ============================================================


print("\n")

print("="*60)
print("RESULTADO FINAL")
print("="*60)


print(resumo)



print("\nArquivos:")

print(SAIDA)

print(RESUMO)



print("\nTempo:")

print(

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)


print("\nFim.")