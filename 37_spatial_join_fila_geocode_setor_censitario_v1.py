# ============================================================
# 37_spatial_join_fila_geocode_setor_censitario_v2.py
#
# GEOCODE -> SETOR CENSITARIO IBGE
#
# Entrada:
# geocode_fila_setor_censitario_v1.csv
#
# Saída:
# geocode_fila_com_CD_SETOR_v2.csv
#
# ============================================================


import geopandas as gpd
import pandas as pd
import os
import time


inicio = time.time()


print("="*60)
print("SPATIAL JOIN FILA GEOCODE SETOR CENSITARIO - V2")
print("="*60)



# ============================================================
# ARQUIVOS
# ============================================================


ENTRADA = (
    "resultados/"
    "geocode_fila_setor_censitario_v1.csv"
)


SAIDA = (
    "resultados/"
    "geocode_fila_com_CD_SETOR_v2.csv"
)


RESUMO = (
    "resultados/"
    "resumo_spatial_fila_setor_v2.csv"
)



# ============================================================
# LOCALIZAR SHAPEFILE
# ============================================================


print("\nProcurando shapefile de setores...")


possiveis = [

    "resultados_02/joinville_setores_mapa.shp",

    "resultados_03/joinville_setores_mapa.shp",

    "resultados_02/joinville_setores_mapa_final.shp",

    "resultados_02/setores_consumo_p99_final.shp",

    "dados/joinville_setores_mapa.shp"

]


SHAPEFILE = None


for arquivo in possiveis:


    if os.path.exists(arquivo):

        SHAPEFILE = arquivo

        break



if SHAPEFILE is None:


    raise FileNotFoundError(

        """
        Nenhum shapefile encontrado.

        Verifique onde está o arquivo:
        joinville_setores_mapa.shp

        """

    )


print(

    "Shapefile encontrado:",

    SHAPEFILE

)



# ============================================================
# LER GEOCODE
# ============================================================


print("\nLendo geocodificação...")


df = pd.read_csv(

    ENTRADA,

    low_memory=False

)



print(

    "Total:",

    len(df)

)



# somente encontrados


df = df[

    df["status_geocode"]

    =="encontrado"

].copy()



print(

    "Com coordenadas:",

    len(df)

)



# ============================================================
# CRIAR PONTOS
# ============================================================


print("\nCriando pontos...")


pontos = gpd.GeoDataFrame(

    df,

    geometry=gpd.points_from_xy(

        df["longitude"],

        df["latitude"]

    ),

    crs="EPSG:4326"

)



print(

    "Pontos:",

    len(pontos)

)



# ============================================================
# LER SETORES
# ============================================================


print("\nLendo setores censitários...")


setores = gpd.read_file(

    SHAPEFILE

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

        "A malha não possui CD_SETOR"

    )


print("CD_SETOR OK")



# ============================================================
# CRS
# ============================================================


print("\nAjustando projeção...")


if setores.crs != pontos.crs:


    pontos = pontos.to_crs(

        setores.crs

    )



# ============================================================
# SPATIAL JOIN
# ============================================================


print("\nExecutando spatial join...")


join = gpd.sjoin(

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

    "Resultado join:",

    len(join)

)



# ============================================================
# CLASSIFICAÇÃO
# ============================================================


join["metodo_setor"] = None

join["confianca"] = None



mask = join["CD_SETOR"].notna()



join.loc[

    mask,

    "metodo_setor"

] = "spatial_join_geocode"



join.loc[

    mask,

    "confianca"

] = "ALTA"



join.loc[

    ~mask,

    "metodo_setor"

] = "sem_setor"



join.loc[

    ~mask,

    "confianca"

] = "NULA"



# ============================================================
# REMOVER GEOMETRIA
# ============================================================


resultado = join.drop(

    columns=[

        "geometry",

        "index_right"

    ],

    errors="ignore"

)



# ============================================================
# RESUMO
# ============================================================


resumo = pd.DataFrame({

    "indicador":[

        "pontos_processados",

        "com_CD_SETOR",

        "sem_CD_SETOR",

        "percentual_sucesso"

    ],

    "valor":[

        len(resultado),

        resultado["CD_SETOR"].notna().sum(),

        resultado["CD_SETOR"].isna().sum(),

        round(

            resultado["CD_SETOR"]

            .notna()

            .mean()

            *

            100,

            2

        )

    ]

})



# ============================================================
# SALVAR
# ============================================================


print("\nSalvando arquivos...")


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