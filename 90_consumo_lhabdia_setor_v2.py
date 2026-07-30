# ============================================================
# 90_consumo_lhabdia_setor_v2.py
#
# CONSUMO DE ÁGUA POR SETOR CENSITÁRIO
#
# CAJ + CENSO 2022
#
# Entradas:
#   resultados/matricula_setor_qgis.csv
#   Agregados_preliminares_por_setores_censitarios_SC (1).csv
#   joinville_setores_mapa.shp
#
# Saídas:
#   consumo_lhabdia_setor.csv
#   consumo_lhabdia_setor.shp
#   resumo_consumo_setor.xlsx
#
# ============================================================


import os
import time
import warnings

import pandas as pd
import geopandas as gpd


warnings.filterwarnings("ignore")


inicio = time.time()


print("="*70)
print("CONSUMO L/HAB/DIA POR SETOR CENSITÁRIO")
print("="*70)



RESULTADOS = "resultados"



arquivo_consumo = os.path.join(
    RESULTADOS,
    "matricula_setor_qgis.csv"
)


arquivo_pop = (
    "Agregados_preliminares_por_setores_censitarios_SC (1).csv"
)


arquivo_shp = (
    "joinville_setores_mapa.shp"
)



# ============================================================
# LER CONSUMO
# ============================================================


print("\nLendo consumo...")


df = pd.read_csv(
    arquivo_consumo,
    encoding="utf-8-sig",
    low_memory=False
)


print(
    "Registros:",
    len(df)
)



# setor

campo_setor = None


for c in [
    "CD_SETOR_FINAL",
    "CD_SETOR"
]:

    if c in df.columns:

        campo_setor = c
        break



if campo_setor is None:

    raise Exception(
        "Campo setor não encontrado."
    )



print(
    "Campo setor:",
    campo_setor
)



df["CD_SETOR"] = (

    df[campo_setor]
    .astype(str)
    .str.replace(".0","",regex=False)
    .str.strip()

)



# ============================================================
# IDENTIFICAR CONSUMO
# ============================================================


print("\nIdentificando consumo...")


col_consumo = None


for c in df.columns:

    if "CONSUMO" in c.upper():

        col_consumo = c
        break



if col_consumo is None:

    raise Exception(
        "Não encontrou coluna de consumo."
    )


print(
    "Coluna consumo:",
    col_consumo
)



# ============================================================
# AGREGAR CONSUMO
# ============================================================


print("\nAgregando setores...")


setor = (

    df.groupby("CD_SETOR")

    .agg(

        MATRICULAS=(
            "Matricula",
            "nunique"
        ),

        REGISTROS=(
            "Matricula",
            "count"
        ),

        CONSUMO_TOTAL=(
            col_consumo,
            "sum"
        )

    )

    .reset_index()

)



print(
    "Setores consumo:",
    len(setor)
)



# ============================================================
# POPULAÇÃO IBGE
# ============================================================


print("\nLendo população IBGE...")


pop = pd.read_csv(

    arquivo_pop,

    sep=";",

    encoding="latin1",

    low_memory=False

)



print(
    "Setores IBGE:",
    len(pop)
)



pop["CD_SETOR"] = (

    pop["CD_SETOR"]

    .astype(str)

    .str.replace(

        "P",

        "",

        regex=False

    )

    .str.strip()

)



pop = pop[

    [

        "CD_SETOR",

        "v0001"

    ]

].copy()



pop.rename(

    columns={

        "v0001":

        "POPULACAO"

    },

    inplace=True

)



# ============================================================
# CRUZAMENTO
# ============================================================


print("\nCruzando população...")


base = setor.merge(

    pop,

    on="CD_SETOR",

    how="left"

)



print(

    "Com população:",

    base["POPULACAO"]

    .notna()

    .sum()

)



# ============================================================
# CALCULO
# ============================================================


print("\nCalculando L/hab/dia...")


MESES = 26

DIAS = 30



base["CONSUMO_M3_MES"] = (

    base["CONSUMO_TOTAL"]

    /

    MESES

)



base["L_HAB_DIA"] = (

    base["CONSUMO_M3_MES"]

    *

    1000

    /

    (

        base["POPULACAO"]

        *

        DIAS

    )

)



# ============================================================
# SHAPE
# ============================================================


print("\nAdicionando geometria...")


gdf = gpd.read_file(

    arquivo_shp

)



gdf["CD_SETOR"] = (

    gdf["CD_SETOR"]

    .astype(str)

    .str.strip()

)



mapa = gdf.merge(

    base,

    on="CD_SETOR",

    how="left"

)



# ============================================================
# EXPORTAR
# ============================================================


print("\nSalvando...")


csv_saida = os.path.join(

    RESULTADOS,

    "consumo_lhabdia_setor.csv"

)



shp_saida = os.path.join(

    RESULTADOS,

    "consumo_lhabdia_setor.shp"

)



xlsx_saida = os.path.join(

    RESULTADOS,

    "resumo_consumo_setor.xlsx"

)



mapa.drop(

    columns="geometry"

).to_csv(

    csv_saida,

    index=False,

    encoding="utf-8-sig"

)



mapa.to_file(

    shp_saida,

    encoding="utf-8"

)



(

    mapa.drop(columns="geometry")

    .sort_values(

        "L_HAB_DIA",

        ascending=False

    )

    .to_excel(

        xlsx_saida,

        index=False

    )

)



print("\nResumo final")

print(
    "Setores:",
    len(mapa)
)


print(
    "Setores com consumo:",
    mapa["CONSUMO_TOTAL"]
    .notna()
    .sum()
)


print(
    "Setores com L/hab/dia:",
    mapa["L_HAB_DIA"]
    .notna()
    .sum()
)



print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim Código 90.")