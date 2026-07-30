# ============================================================
# 92_consumo_setor_qgis.py
#
# CONSUMO ÁGUA x SETOR CENSITÁRIO
#
# Entrada:
#   fev20 a mar22.csv
#   abr22 a maio24.csv
#   resultados/matricula_setor_qgis.csv
#   Agregados_preliminares_por_setores_censitarios_SC (1).csv
#
# Saída:
#   resultados/consumo_setor_lhabdia.csv
#
# ============================================================


import os
import time
import warnings

import pandas as pd


warnings.filterwarnings("ignore")


inicio = time.time()


print("="*70)
print("CONSUMO ÁGUA x SETOR CENSITÁRIO")
print("="*70)



RESULTADOS = "resultados"


arquivo_consumo1 = "fev20 a mar22.csv"

arquivo_consumo2 = "abr22 a maio24.csv"


arquivo_setor = os.path.join(
    RESULTADOS,
    "matricula_setor_qgis.csv"
)


arquivo_pop = (
    "Agregados_preliminares_por_setores_censitarios_SC (1).csv"
)



# ============================================================
# FUNÇÕES
# ============================================================


def limpar_colunas(df):

    df.columns = (

        df.columns

        .astype(str)

        .str.strip()

        .str.upper()

        .str.replace(
            "Ï»¿",
            "",
            regex=False
        )

        .str.replace(
            " ",
            "_",
            regex=False
        )

    )

    return df



def normalizar_codigo(x):

    if pd.isna(x):

        return ""

    x = str(x)

    x = x.replace(
        ".0",
        ""
    )

    x = x.replace(
        "P",
        ""
    )

    return x.zfill(15)



# ============================================================
# LER CONSUMO
# ============================================================


print("\nLendo consumo...")


def ler_consumo(arq):

    print("\nArquivo:")
    print(arq)


    df = pd.read_csv(

        arq,

        sep=";",

        encoding="latin1",

        low_memory=False

    )


    df = limpar_colunas(df)


    print(
        "Registros:",
        len(df)
    )


    return df



c1 = ler_consumo(
    arquivo_consumo1
)


c2 = ler_consumo(
    arquivo_consumo2
)



consumo = pd.concat(

    [
        c1,
        c2
    ],

    ignore_index=True

)



print(
    "\nTotal registros consumo:",
    len(consumo)
)



print("\nColunas consumo:")

for c in consumo.columns:

    print("-",c)



# ============================================================
# CONSUMO MÉDIO
# ============================================================


print("\nCalculando consumo...")


meses = [

    c for c in consumo.columns

    if "MICROMEDIDO" in c

]



print(
    "Meses encontrados:",
    len(meses)
)



consumo[meses] = consumo[meses].apply(

    pd.to_numeric,

    errors="coerce"

)



consumo["CONSUMO_MEDIO_MES"] = (

    consumo[meses]

    .mean(

        axis=1,

        skipna=True

    )

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



# ============================================================
# LER MATRÍCULA x SETOR
# ============================================================


print("\nLendo associação matrícula setor...")


setores = pd.read_csv(

    arquivo_setor,

    encoding="utf-8-sig",

    low_memory=False

)



setores = limpar_colunas(setores)



print("\nColunas setor:")

for c in setores.columns:

    print("-",c)



# garantir matrícula


if "MATRICULA" not in setores.columns:

    raise Exception(
        "Campo MATRÍCULA não encontrado na base setor"
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

    base["CD_SETOR_FINAL"].notna()

].copy()



print(

    "Com setor:",

    len(base)

)



# ============================================================
# AGREGAR SETORES
# ============================================================


print("\nAgregando setores...")


setor = (

    base.groupby(

        "CD_SETOR_FINAL"

    )

    .agg(

        MATRICULAS=(

            "MATRICULA",

            "nunique"

        ),

        CONSUMO_MEDIO_MES=(

            "CONSUMO_MEDIO_MES",

            "sum"

        )

    )

    .reset_index()

)



setor["CONSUMO_L_DIA"] = (

    setor["CONSUMO_MEDIO_MES"]

    *

    1000

    /

    30

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



pop = limpar_colunas(pop)



print("\nColunas população:")

for c in pop.columns:

    print("-",c)



pop["CD_SETOR"] = (

    pop["CD_SETOR"]

    .astype(str)

    .str.replace(
        '"',
        "",
        regex=False
    )

    .str.replace(
        "P",
        "",
        regex=False
    )

    .str.zfill(15)

)



pop["POPULACAO"] = pd.to_numeric(

    pop["V0001"],

    errors="coerce"

)



pop = pop[

    [

        "CD_SETOR",

        "POPULACAO"

    ]

]



# ============================================================
# NORMALIZAR SETORES CAJ
# ============================================================


setor["CD_SETOR_FINAL"] = (

    setor["CD_SETOR_FINAL"]

    .apply(normalizar_codigo)

)



# ============================================================
# JOIN POPULAÇÃO
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
# L/HAB/DIA
# ============================================================


print("\nCalculando L/hab/dia...")


final["L_HAB_DIA"] = (

    final["CONSUMO_L_DIA"]

    /

    final["POPULACAO"]

)



# ============================================================
# SALVAR
# ============================================================


saida = os.path.join(

    RESULTADOS,

    "consumo_setor_lhabdia.csv"

)



final.to_csv(

    saida,

    index=False,

    encoding="utf-8-sig"

)



print("\nArquivo criado:")

print(saida)



print("\nResumo:")

print(final.head())



print(

    "\nQuantidade setores:",

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



print("\nFim Código 92.")