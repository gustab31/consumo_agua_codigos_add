# ============================================================
# 33_spatial_join_setor_censitario_v3.py
#
# ETAPA:
# Recuperação espacial de CD_SETOR
#
# Unidade:
# SETOR CENSITÁRIO IBGE
#
# ============================================================


import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import glob
import os
import time


inicio = time.time()


print("="*60)
print("SPATIAL JOIN SETOR CENSITÁRIO - V3")
print("="*60)



# ============================================================
# ARQUIVOS
# ============================================================


BASE = (
    "resultados/"
    "base_residencial_setor_logradouro_dominante_v1.csv"
)


GEOCODES = [

    "resultados/geocode_prioridade_alta_resultado.csv",

    "resultados/geocode_fila_prioridade_v2_resultado.csv"

]


SAIDA = (

    "resultados/"
    "base_residencial_setor_espacial_v3.csv"

)


RESUMO = (

    "resultados/"
    "resumo_espacial_setor_v3.csv"

)



# ============================================================
# FUNÇÃO CHAVE ENDEREÇO
# ============================================================


def criar_chave(df):


    colunas = df.columns.tolist()


    # prioridade para chave existente

    for c in [

        "CHAVE_END_BAIRRO",

    ]:

        if c in colunas:

            return (

                df[c]

                .astype(str)

                .str.upper()

                .str.strip()

            )



    endereco = None

    bairro = None



    for c in [

        "endereco",

        "Endereco",

        "ENDERECO"

    ]:

        if c in colunas:

            endereco = c

            break



    for c in [

        "bairro",

        "Bairro",

        "BAIRRO"

    ]:

        if c in colunas:

            bairro = c

            break



    if endereco is None:

        raise Exception(

            "Coluna de endereco nao encontrada\n"

            + str(colunas)

        )


    if bairro is None:

        raise Exception(

            "Coluna de bairro nao encontrada\n"

            + str(colunas)

        )



    return (

        df[endereco]

        .astype(str)

        .str.upper()

        .str.strip()

        +

        "_"

        +

        df[bairro]

        .astype(str)

        .str.upper()

        .str.strip()

    )



# ============================================================
# LER BASE
# ============================================================


print("\nLendo base...")


df = pd.read_csv(

    BASE,

    low_memory=False

)



print(

    "Shape:",

    df.shape

)



print(

    "Colunas:",

    df.columns.tolist()

)



if "CD_SETOR" not in df.columns:

    df["CD_SETOR"] = None



antes = df["CD_SETOR"].notna().sum()


print(

    "Com CD_SETOR antes:",

    antes

)



# ============================================================
# LER GEOCODIFICAÇÕES
# ============================================================


print("\nLendo geocodificações...")


geo_lista=[]



for arquivo in GEOCODES:


    if os.path.exists(arquivo):


        print(

            "Encontrado:",

            arquivo

        )


        temp = pd.read_csv(

            arquivo,

            low_memory=False

        )


        print(

            "Linhas:",

            len(temp)

        )


        print(

            "Colunas:",

            temp.columns.tolist()

        )


        geo_lista.append(temp)



if len(geo_lista)==0:

    raise Exception(

        "Nenhum arquivo de geocodificação encontrado"

    )



geo = pd.concat(

    geo_lista,

    ignore_index=True

)



print(

    "\nTotal geocodes:",

    len(geo)

)

# ============================================================
# CRIAR CHAVE E JUNTAR COORDENADAS
# ============================================================


print("\nCriando chaves...")


df["CHAVE_TMP"] = criar_chave(df)

geo["CHAVE_TMP"] = criar_chave(geo)



print(

    "Chaves base:",

    df["CHAVE_TMP"].nunique()

)


print(

    "Chaves geocode:",

    geo["CHAVE_TMP"].nunique()

)



# manter somente coordenadas válidas

geo = geo[

    geo["latitude"].notna()

    &

    geo["longitude"].notna()

].copy()



geo = geo.drop_duplicates(

    "CHAVE_TMP"

)



print(

    "Geocodes válidos:",

    len(geo)

)



# ============================================================
# MERGE COORDENADAS
# ============================================================


print("\nTransferindo coordenadas...")


df = df.merge(

    geo[

        [

            "CHAVE_TMP",

            "latitude",

            "longitude"

        ]

    ],

    on="CHAVE_TMP",

    how="left",

    suffixes=("","_novo")

)



print(

    "Registros com coordenada:",

    df["latitude"].notna().sum()

)



# ============================================================
# CRIAR PONTOS
# ============================================================


print("\nCriando pontos...")


pontos_df = df[

    df["latitude"].notna()

    &

    df["longitude"].notna()

].copy()



pontos = gpd.GeoDataFrame(

    pontos_df,

    geometry=[

        Point(x,y)

        for x,y in zip(

            pontos_df["longitude"],

            pontos_df["latitude"]

        )

    ],

    crs="EPSG:4326"

)



print(

    "Pontos criados:",

    len(pontos)

)



# ============================================================
# LOCALIZAR SHAPEFILE SETORES
# ============================================================


print("\nProcurando setores censitários...")


shps = glob.glob(

    "**/*.shp",

    recursive=True

)



setor_path = None



for shp in shps:


    try:

        teste = gpd.read_file(shp)


        if "CD_SETOR" in teste.columns:

            setor_path = shp

            break


    except Exception:

        continue



if setor_path is None:


    raise Exception(

        "Nenhum shapefile com CD_SETOR encontrado"

    )



print(

    "Shapefile escolhido:",

    setor_path

)



# ============================================================
# LER SETORES IBGE
# ============================================================


setores = gpd.read_file(

    setor_path

)



print(

    "Quantidade setores:",

    len(setores)

)


print(

    "Colunas:",

    setores.columns.tolist()

)



if "CD_SETOR" not in setores.columns:


    raise Exception(

        "Setor sem CD_SETOR"

    )



# ============================================================
# AJUSTAR CRS
# ============================================================


if setores.crs != pontos.crs:


    print(

        "Ajustando CRS..."

    )


    pontos = pontos.to_crs(

        setores.crs

    )



# ============================================================
# SPATIAL JOIN
# ============================================================


print("\nExecutando spatial join...")


resultado = gpd.sjoin(

    pontos,

    setores[

        [

            "CD_SETOR",

            "geometry"

        ]

    ],

    how="left",

    predicate="within"

)



print(

    "Pontos dentro de setor:",

    resultado["CD_SETOR_right"].notna().sum()

)



# ============================================================
# APLICAR APENAS NOS SEM SETOR
# ============================================================


print("\nTransferindo CD_SETOR...")


novos = 0



for idx,row in resultado.iterrows():


    setor_novo = row["CD_SETOR_right"]


    if pd.notna(setor_novo):


        original = row["index"]


        if pd.isna(

            df.loc[

                original,

                "CD_SETOR"

            ]

        ):


            df.loc[

                original,

                "CD_SETOR"

            ] = setor_novo



            df.loc[

                original,

                "metodo_setor"

            ] = (

                "espacial_setor_censitario"

            )


            novos += 1

# ============================================================
# RESULTADO FINAL
# ============================================================


depois = df["CD_SETOR"].notna().sum()


sem = len(df) - depois


percentual = round(

    depois / len(df) * 100,

    2

)



resumo = pd.DataFrame({

    "indicador":[

        "total_registros",

        "com_CD_SETOR_antes",

        "novos_espacial",

        "com_CD_SETOR_depois",

        "sem_CD_SETOR",

        "percentual_cobertura"

    ],

    "valor":[

        len(df),

        antes,

        novos,

        depois,

        sem,

        percentual

    ]

})



# ============================================================
# SALVAR
# ============================================================


print("\nSalvando arquivos...")


df.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)



resumo.to_csv(

    RESUMO,

    index=False,

    encoding="utf-8-sig"

)



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