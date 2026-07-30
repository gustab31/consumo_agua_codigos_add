# ============================================================
# 60_inferencia_vizinhanca_geografica.py
#
# Inferência espacial de setor censitário
#
# Correções:
# - força CD_SETOR_FINAL como string
# - usa joinville_setores_mapa.shp
# - junta coordenadas geocodificadas
# - evita erros pandas float64/string
#
# ============================================================

import os
import time
import glob
import re
import unicodedata

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


inicio = time.time()


print("="*70)
print("INFERÊNCIA ESPACIAL POR VIZINHANÇA GEOGRÁFICA")
print("="*70)



# ------------------------------------------------------------
# arquivos
# ------------------------------------------------------------

BASE = (
    "resultados/"
    "base_setor_final_CEP.csv"
)

GEO = (
    "resultados/"
    "enderecos_geocodificados.csv"
)


SAIDA = (
    "resultados/"
    "inferencia_espacial_geografica.csv"
)


RESUMO = (
    "resultados/"
    "resumo_inferencia_espacial_geografica.csv"
)



# ------------------------------------------------------------
# normalização
# ------------------------------------------------------------

def normalizar(valor):

    if pd.isna(valor):
        return ""

    valor = str(valor).upper()

    valor = (
        unicodedata
        .normalize(
            "NFKD",
            valor
        )
        .encode(
            "ASCII",
            "ignore"
        )
        .decode(
            "ASCII"
        )
    )

    valor = re.sub(
        r"[^A-Z0-9 ]",
        " ",
        valor
    )

    valor = re.sub(
        r"\s+",
        " ",
        valor
    )

    return valor.strip()



# ------------------------------------------------------------
# shapefile correto
# ------------------------------------------------------------

print("\nProcurando shapefile...")


possiveis_shapes = [

    "joinville_setores_mapa.shp",

    "resultados_02/joinville_setores_mapa.shp",

    "resultados_03/joinville_setores_mapa.shp"

]


SHAPE = None


for s in possiveis_shapes:

    if os.path.exists(s):

        SHAPE = s

        break



if SHAPE is None:

    encontrados = glob.glob(
        "**/joinville_setores_mapa.shp",
        recursive=True
    )

    if encontrados:

        SHAPE = encontrados[0]



if SHAPE is None:

    raise Exception(
        "joinville_setores_mapa.shp não encontrado"
    )


print(
    "Shape:",
    SHAPE
)



# ------------------------------------------------------------
# leitura base
# ------------------------------------------------------------

print("\nLendo base final...")


df = pd.read_csv(
    BASE,
    low_memory=False
)


print(
    "Registros:",
    len(df)
)



# ------------------------------------------------------------
# corrigir setor imediatamente
# ------------------------------------------------------------

if "CD_SETOR_FINAL" in df.columns:

    df["CD_SETOR_FINAL"] = (
        df["CD_SETOR_FINAL"]
        .astype("string")
    )

else:

    df["CD_SETOR_FINAL"] = pd.Series(
        pd.NA,
        index=df.index,
        dtype="string"
    )



# ------------------------------------------------------------
# leitura geocodificação
# ------------------------------------------------------------

print("\nLendo geocodificação...")


geo = pd.read_csv(
    GEO,
    low_memory=False
)


print(
    "Geocodificados:",
    len(geo)
)



# ------------------------------------------------------------
# criar chave
# ------------------------------------------------------------

print("\nCriando chave de endereço...")


def criar_chave(df):

    if "Endereco" in df.columns:

        return (
            df["Endereco"]
            .apply(normalizar)
        )

    if "ENDERECO" in df.columns:

        return (
            df["ENDERECO"]
            .apply(normalizar)
        )

    return pd.Series(
        "",
        index=df.index
    )



df["CHAVE_END"] = criar_chave(df)

geo["CHAVE_END"] = criar_chave(geo)



# ------------------------------------------------------------
# coordenadas
# ------------------------------------------------------------

print("\nJuntando coordenadas...")


geo_coord = geo.copy()


geo_coord = geo_coord[

    [
        "CHAVE_END",
        "latitude",
        "longitude"
    ]

]


geo_coord = (
    geo_coord
    .drop_duplicates(
        "CHAVE_END"
    )
)



df = df.merge(

    geo_coord,

    on="CHAVE_END",

    how="left"

)



df["latitude"] = pd.to_numeric(
    df["latitude"],
    errors="coerce"
)


df["longitude"] = pd.to_numeric(
    df["longitude"],
    errors="coerce"
)



print(
    "Com coordenadas:",
    df["latitude"].notna().sum()
)



validos = df[

    df["latitude"].notna()
    &
    df["longitude"].notna()

].copy()


print(
    "Pontos válidos:",
    len(validos)
)


if len(validos)==0:

    raise Exception(
        "Nenhuma coordenada encontrada."
    )



gdf = gpd.GeoDataFrame(

    validos,

    geometry=[

        Point(x,y)

        for x,y in zip(

            validos["longitude"],

            validos["latitude"]

        )

    ],

    crs="EPSG:4326"

)

# ------------------------------------------------------------
# 60_inferencia_vizinhanca_geografica.py
# PARTE 2/2
# ------------------------------------------------------------


# ------------------------------------------------------------
# leitura setores
# ------------------------------------------------------------

print("\nLendo setores censitários...")


setores = gpd.read_file(
    SHAPE
)


print(
    "Quantidade de setores:",
    len(setores)
)


print(
    "\nCampos disponíveis:"
)

print(
    list(setores.columns)
)



# ------------------------------------------------------------
# localizar código setor
# ------------------------------------------------------------

campo_setor = None


for c in [

    "CD_SETOR",

    "CD_GEOCODI",

    "GEOCODIGO",

    "COD_SETOR",

    "SETOR"

]:

    if c in setores.columns:

        campo_setor = c

        break



if campo_setor is None:

    raise Exception(
        """
Não foi encontrado campo de código de setor.
Confira os campos acima.
"""
    )


print(
    "\nCampo setor:",
    campo_setor
)



setores = setores[

    [

        campo_setor,

        "geometry"

    ]

]


setores = setores.rename(

    columns={

        campo_setor:
        "SETOR_ESPACIAL"

    }

)



# ------------------------------------------------------------
# garantir tipos
# ------------------------------------------------------------

setores["SETOR_ESPACIAL"] = (

    setores["SETOR_ESPACIAL"]

    .astype("string")

)



# ------------------------------------------------------------
# reprojeção
# ------------------------------------------------------------

print(
    "\nPreparando projeção..."
)


gdf = gdf.to_crs(
    setores.crs
)



# ------------------------------------------------------------
# spatial join
# ------------------------------------------------------------

print(
    "\nExecutando junção espacial..."
)


resultado = gpd.sjoin(

    gdf,

    setores,

    how="left",

    predicate="within"

)



print(
    "Pontos relacionados:",
    resultado["SETOR_ESPACIAL"].notna().sum()
)



# ------------------------------------------------------------
# corrigir setor antes da atribuição
# ------------------------------------------------------------

if "CD_SETOR_FINAL" not in resultado.columns:

    resultado["CD_SETOR_FINAL"] = pd.Series(

        pd.NA,

        index=resultado.index,

        dtype="string"

    )

else:

    resultado["CD_SETOR_FINAL"] = (

        resultado["CD_SETOR_FINAL"]

        .astype("string")

    )



resultado["SETOR_ANTES"] = (

    resultado["CD_SETOR_FINAL"]

    .copy()

)



resultado["SETOR_ESPACIAL"] = (

    resultado["SETOR_ESPACIAL"]

    .astype("string")

)



# ------------------------------------------------------------
# aplicar inferência
# ------------------------------------------------------------

resultado["METODO_ESPACIAL"] = (
    "SEM_INFERENCIA"
)



mask = (

    resultado["SETOR_ANTES"].isna()

    &

    resultado["SETOR_ESPACIAL"].notna()

)



print(
    "\nNovas inferências:",
    mask.sum()
)



resultado.loc[

    mask,

    "CD_SETOR_FINAL"

] = (

    resultado.loc[

        mask,

        "SETOR_ESPACIAL"

    ]

    .astype("string")

)



resultado.loc[

    mask,

    "METODO_ESPACIAL"

] = (

    "PONTO_DENTRO_SETOR"

)



# ------------------------------------------------------------
# resumo
# ------------------------------------------------------------

resumo = pd.DataFrame({

    "indicador":[

        "total_registros_base",

        "registros_com_coordenada",

        "pontos_dentro_setor",

        "novas_inferencias",

        "sem_inferencia"

    ],

    "valor":[

        len(df),

        len(validos),

        int(resultado["SETOR_ESPACIAL"].notna().sum()),

        int(mask.sum()),

        int(len(df)-mask.sum())

    ]

})



print("\n")
print("="*70)
print("RESULTADO FINAL")
print("="*70)


print(resumo)



# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

os.makedirs(

    "resultados",

    exist_ok=True

)



resultado = resultado.drop(

    columns=[

        "geometry",

        "index_right"

    ],

    errors="ignore"

)



resultado.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)



resumo.to_csv(

    RESUMO,

    index=False,

    encoding="utf-8-sig"

)



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