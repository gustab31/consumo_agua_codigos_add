# ============================================================
# 98_gerar_mapa_consumo_lhabdia_filtrado.py
#
# GERA MAPA CONSUMO L/hab/dia FILTRADO
#
# Entrada:
# resultados_04/consumo_lhabdia_setores.csv
# joinville_setores_mapa.shp
#
# Saídas:
# resultados_04/
#   consumo_lhabdia_filtrado.csv
#   mapa_consumo_lhabdia_filtrado.shp
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
print("MAPA CONSUMO L/hab/dia FILTRADO")
print("="*70)


PASTA = "resultados_04"


arquivo_csv = os.path.join(
    PASTA,
    "consumo_lhabdia_setores.csv"
)


arquivo_shp = "joinville_setores_mapa.shp"



# ============================================================
# LER DADOS
# ============================================================


print("\nLendo consumo...")


df = pd.read_csv(

    arquivo_csv,

    encoding="utf-8-sig",

    low_memory=False

)



print(

    "Setores:",

    len(df)

)



# ============================================================
# PADRONIZAR SETOR
# ============================================================


df["CD_SETOR_FINAL"] = (

    df["CD_SETOR_FINAL"]

    .astype(str)

    .str.replace(

        ".0",

        "",

        regex=False

    )

    .str.strip()

)



# ============================================================
# IDENTIFICAR SUSPEITOS
# ============================================================


print("\nIdentificando setores suspeitos...")


df["SETOR_SUSPEITO"] = False



df.loc[

    df["POPULACAO"] < 100,

    "SETOR_SUSPEITO"

] = True



df.loc[

    df["L_HAB_DIA"] > 500,

    "SETOR_SUSPEITO"

] = True



# ============================================================
# CRIAR INDICADOR FILTRADO
# ============================================================


df["L_HAB_DIA_FILTRADO"] = (

    df["L_HAB_DIA"]

)



df.loc[

    df["SETOR_SUSPEITO"],

    "L_HAB_DIA_FILTRADO"

] = None



# ============================================================
# CLASSES
# ============================================================


def classificar(valor):

    if pd.isna(valor):

        return "Sem classificação"

    elif valor < 50:

        return "Muito baixo"

    elif valor < 100:

        return "Baixo"

    elif valor < 200:

        return "Normal"

    elif valor < 300:

        return "Elevado"

    else:

        return "Muito elevado"



df["CLASSE_BRUTA"] = (

    df["L_HAB_DIA"]

    .apply(classificar)

)



df["CLASSE_FILTRADA"] = (

    df["L_HAB_DIA_FILTRADO"]

    .apply(classificar)

)



# ============================================================
# EXPORTAR CSV
# ============================================================


saida_csv = os.path.join(

    PASTA,

    "consumo_lhabdia_filtrado.csv"

)


df.to_csv(

    saida_csv,

    index=False,

    encoding="utf-8-sig"

)



# ============================================================
# SHAPEFILE
# ============================================================


print("\nLendo shapefile...")


gdf = gpd.read_file(

    arquivo_shp

)



gdf["CD_SETOR"] = (

    gdf["CD_SETOR"]

    .astype(str)

    .str.replace(

        ".0",

        "",

        regex=False

    )

    .str.strip()

)



mapa = gdf.merge(

    df,

    left_on="CD_SETOR",

    right_on="CD_SETOR_FINAL",

    how="left"

)



saida_shp = os.path.join(

    PASTA,

    "mapa_consumo_lhabdia_filtrado.shp"

)



mapa.to_file(

    saida_shp,

    encoding="utf-8"

)



# ============================================================
# RESUMO
# ============================================================


print("\n==============================")
print("ARQUIVOS GERADOS")
print("==============================")


print(saida_csv)

print(saida_shp)



print("\nResumo:")


print(

    "Setores totais:",

    len(df)

)


print(

    "Setores suspeitos:",

    df["SETOR_SUSPEITO"].sum()

)


print(

    "Setores válidos:",

    (~df["SETOR_SUSPEITO"]).sum()

)



print("\nDistribuição filtrada:")


print(

    df["CLASSE_FILTRADA"]

    .value_counts()

)



print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim Código 98.")