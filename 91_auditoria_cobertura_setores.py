# ============================================================
# 91_auditoria_cobertura_setores.py
#
# AUDITORIA COBERTURA CONSUMO CAJ x SETORES IBGE
#
# Entradas:
#   resultados\matricula_setor_qgis.csv
#   joinville_setores_mapa.shp
#
# Saídas:
#   resultados\auditoria_cobertura_setores.xlsx
#   resultados\setores_sem_consumo.csv
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
print("AUDITORIA COBERTURA CONSUMO x SETOR CENSITÁRIO")
print("="*70)


RESULTADOS = "resultados"


arquivo_consumo = os.path.join(
    RESULTADOS,
    "matricula_setor_qgis.csv"
)


arquivo_shp = "joinville_setores_mapa.shp"



# ============================================================
# LER CONSUMO
# ============================================================


print("\nLendo consumo...")


df = pd.read_csv(
    arquivo_consumo,
    encoding="utf-8-sig",
    low_memory=False
)


print("Registros:", len(df))


print("\nColunas:")
for c in df.columns:
    print("-", c)



# escolher setor

campo_setor = None


for c in [
    "CD_SETOR_FINAL",
    "CD_SETOR",
]:

    if c in df.columns:
        campo_setor = c
        break


if campo_setor is None:

    raise Exception(
        "Campo de setor não encontrado"
    )


print(
    "\nCampo setor:",
    campo_setor
)



df[campo_setor] = (
    df[campo_setor]
    .astype(str)
    .str.replace(".0","",regex=False)
    .str.zfill(15)
)



# ============================================================
# RESUMO CONSUMO
# ============================================================


setores_caj = (
    df[campo_setor]
    .dropna()
    .unique()
)


print(
    "\nSetores com CAJ:",
    len(setores_caj)
)



# bairros

if "Bairro" in df.columns:

    bairros = (
        df.groupby("Bairro")
        .size()
        .reset_index(name="MATRICULAS")
    )


else:

    bairros = pd.DataFrame()



# ============================================================
# LER IBGE
# ============================================================


print("\nLendo setores IBGE...")


gdf = gpd.read_file(
    arquivo_shp
)


print(
    "Setores IBGE:",
    len(gdf)
)



gdf["CD_SETOR"] = (
    gdf["CD_SETOR"]
    .astype(str)
    .str.zfill(15)
)



# ============================================================
# CLASSIFICAR
# ============================================================


gdf["TEM_CONSUMO_CAJ"] = (
    gdf["CD_SETOR"]
    .isin(setores_caj)
)



print("\nDistribuição:")

print(
    gdf["TEM_CONSUMO_CAJ"]
    .value_counts()
)



# ============================================================
# SETORES SEM CONSUMO
# ============================================================


sem_consumo = gdf[
    ~gdf["TEM_CONSUMO_CAJ"]
].copy()



# ============================================================
# SETORES COM CONSUMO
# ============================================================


com_consumo = gdf[
    gdf["TEM_CONSUMO_CAJ"]
].copy()



# ============================================================
# EXPORTAR
# ============================================================


saida_excel = os.path.join(
    RESULTADOS,
    "auditoria_cobertura_setores.xlsx"
)



saida_csv = os.path.join(
    RESULTADOS,
    "setores_sem_consumo.csv"
)



with pd.ExcelWriter(
    saida_excel
) as writer:


    com_consumo.drop(
        columns="geometry"
    ).to_excel(
        writer,
        sheet_name="com_consumo",
        index=False
    )


    sem_consumo.drop(
        columns="geometry"
    ).to_excel(
        writer,
        sheet_name="sem_consumo",
        index=False
    )


    bairros.to_excel(
        writer,
        sheet_name="bairros",
        index=False
    )



sem_consumo.drop(
    columns="geometry"
).to_csv(
    saida_csv,
    index=False,
    encoding="utf-8-sig"
)



print("\nArquivos gerados:")
print("-", saida_excel)
print("-", saida_csv)


print("\nResumo final")
print(
    "Setores IBGE:",
    len(gdf)
)

print(
    "Com CAJ:",
    len(com_consumo)
)

print(
    "Sem CAJ:",
    len(sem_consumo)
)


print(
    "\nTempo:",
    round(time.time()-inicio,2),
    "segundos"
)


print("\nFim Código 91.")