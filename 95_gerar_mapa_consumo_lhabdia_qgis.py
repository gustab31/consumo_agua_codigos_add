# ============================================================
# 95_gerar_mapa_consumo_lhabdia_qgis_v2.py
#
# PRODUTO FINAL:
# CONSUMO DE ÁGUA L/hab/dia POR SETOR CENSITÁRIO
#
# Saída:
# resultados_04
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
print("GERAÇÃO MAPA CONSUMO L/hab/dia v2")
print("="*70)



# ============================================================
# PASTA RESULTADO
# ============================================================


RESULTADOS = "resultados_04"


os.makedirs(
    RESULTADOS,
    exist_ok=True
)



# ============================================================
# ARQUIVOS
# ============================================================


arquivo_consumo1 = (
    "fev20 a mar22.csv"
)


arquivo_consumo2 = (
    "abr22 a maio24.csv"
)


arquivo_setor = os.path.join(
    "resultados",
    "matricula_setor_preciso.csv"
)


arquivo_pop = (
    "Agregados_preliminares_por_setores_censitarios_SC (1).csv"
)


arquivo_shp = (
    "joinville_setores_mapa.shp"
)



# ============================================================
# CONSUMO
# ============================================================


print("\nLendo consumo...")


lista = []


for arq in [

    arquivo_consumo1,

    arquivo_consumo2

]:


    print("\nArquivo:")
    print(arq)


    df = pd.read_csv(

        arq,

        sep=";",

        encoding="latin1",

        low_memory=False

    )


    print(
        "Registros:",
        len(df)
    )


    lista.append(df)



consumo = pd.concat(

    lista,

    ignore_index=True

)



print(

    "\nTotal consumo:",

    len(consumo)

)



cols_mes = [

    c for c in consumo.columns

    if "MICROMEDIDO" in c.upper()

]


print(

    "Meses encontrados:",

    len(cols_mes)

)



for c in cols_mes:

    consumo[c] = pd.to_numeric(

        consumo[c],

        errors="coerce"

    )



consumo["CONSUMO_MEDIO_MES"] = (

    consumo[cols_mes]

    .mean(axis=1)

)



consumo["MATRICULA"] = (

    consumo["MATRICULA"]

    .astype(str)

    .str.replace(

        ".0",

        "",

        regex=False

    )

)



consumo = consumo[

    [

        "MATRICULA",

        "CONSUMO_MEDIO_MES"

    ]

]



# ============================================================
# ASSOCIAÇÃO SETOR
# ============================================================


print("\nLendo associação matrícula setor...")


setores = pd.read_csv(

    arquivo_setor,

    encoding="utf-8-sig",

    low_memory=False

)



print(

    setores.columns.tolist()

)



setores.columns = (

    setores.columns

    .str.replace(

        "ï»¿",

        "",

        regex=False

    )

    .str.strip()

    .str.upper()

)



setores["MATRICULA"] = (

    setores["MATRICULA"]

    .astype(str)

    .str.replace(

        ".0",

        "",

        regex=False

    )

)



setores["CD_SETOR_FINAL"] = (

    setores["CD_SETOR_FINAL"]

    .astype(str)

    .str.replace(

        ".0",

        "",

        regex=False

    )

    .str.strip()

)



print(

    "Matrículas setor:",

    len(setores)

)



# ============================================================
# CRUZAMENTO
# ============================================================


print("\nCruzando consumo x setor...")


base = consumo.merge(

    setores[

        [

            "MATRICULA",

            "CD_SETOR_FINAL"

        ]

    ],

    on="MATRICULA",

    how="left"

)



base = base[

    base["CD_SETOR_FINAL"]

    .notna()

]



print(

    "Com setor:",

    len(base)

)



# ============================================================
# AGREGAR
# ============================================================


print("\nAgregando setores...")


setor = (

    base.groupby(

        "CD_SETOR_FINAL"

    )

    .agg(

        MATRICULAS=(

            "MATRICULA",

            "count"

        ),

        CONSUMO_MEDIO_MES=(

            "CONSUMO_MEDIO_MES",

            "sum"

        )

    )

    .reset_index()

)



# ============================================================
# POPULAÇÃO
# ============================================================


print("\nLendo população IBGE...")


pop = pd.read_csv(

    arquivo_pop,

    sep=";",

    encoding="latin1",

    low_memory=False

)



pop.columns = (

    pop.columns

    .str.replace('"',"",regex=False)

    .str.strip()

    .str.upper()

)



print(

    pop.columns.tolist()

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



pop["V0001"] = pd.to_numeric(

    pop["V0001"],

    errors="coerce"

)



pop = pop[

    [

        "CD_SETOR",

        "V0001"

    ]

]



pop = pop.rename(

    columns={

        "V0001":

        "POPULACAO"

    }

)



# ============================================================
# CORREÇÃO CHAVES
# ============================================================


setor["CD_SETOR_FINAL"] = (

    setor["CD_SETOR_FINAL"]

    .astype(str)

    .str.replace(

        ".0",

        "",

        regex=False

    )

    .str.strip()

)



pop["CD_SETOR"] = (

    pop["CD_SETOR"]

    .astype(str)

    .str.strip()

)



# ============================================================
# JUNÇÃO POPULAÇÃO
# ============================================================


print("\nJuntando população...")


final = setor.merge(

    pop,

    left_on="CD_SETOR_FINAL",

    right_on="CD_SETOR",

    how="left"

)



print(

    "Setores sem população:",

    final["POPULACAO"]

    .isna()

    .sum()

)



# ============================================================
# CÁLCULO
# ============================================================


print("\nCalculando L/hab/dia...")


final["CONSUMO_L_DIA"] = (

    final["CONSUMO_MEDIO_MES"]

    *

    1000

    /

    30

)



final["L_HAB_DIA"] = (

    final["CONSUMO_L_DIA"]

    /

    final["POPULACAO"]

)



# ============================================================
# SHAPEFILE
# ============================================================


print("\nLendo setores IBGE...")


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

    final,

    left_on="CD_SETOR",

    right_on="CD_SETOR_FINAL",

    how="left"

)



# ============================================================
# EXPORTAÇÃO
# ============================================================


csv_saida = os.path.join(

    RESULTADOS,

    "consumo_lhabdia_setores.csv"

)


shp_saida = os.path.join(

    RESULTADOS,

    "mapa_consumo_lhabdia_setores.shp"

)



final.to_csv(

    csv_saida,

    index=False,

    encoding="utf-8-sig"

)



mapa.to_file(

    shp_saida,

    encoding="utf-8"

)



# relatório


relatorio = os.path.join(

    RESULTADOS,

    "relatorio_final.txt"

)



with open(

    relatorio,

    "w",

    encoding="utf-8"

) as f:


    f.write(

        "MAPA CONSUMO L/hab/dia\n\n"

    )


    f.write(

        f"Matrículas consumo: {len(consumo)}\n"

    )


    f.write(

        f"Setores consumo: {len(final)}\n"

    )


    f.write(

        f"Sem população: {final['POPULACAO'].isna().sum()}\n"

    )



print("\n==============================")

print("ARQUIVOS GERADOS")

print("==============================")

print(csv_saida)

print(shp_saida)

print(relatorio)



print("\nResumo:")

print(final.head())


print(

    "\nSetores:",

    len(final)

)


print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)


print("\nFim Código 95 v2.")