# ============================================================
# 97_diagnostico_setores_extremos_lhabdia.py
#
# Diagnóstico dos valores extremos de L/hab/dia
#
# Entrada:
# resultados_04/consumo_lhabdia_setores.csv
#
# Saídas:
# resultados_04
#
# ============================================================


import os
import time
import pandas as pd


inicio = time.time()


print("="*70)
print("DIAGNÓSTICO SETORES EXTREMOS L/hab/dia")
print("="*70)



PASTA = "resultados_04"


arquivo = os.path.join(
    PASTA,
    "consumo_lhabdia_setores.csv"
)



# ============================================================
# LEITURA
# ============================================================


print("\nLendo dados...")


df = pd.read_csv(
    arquivo,
    encoding="utf-8-sig",
    low_memory=False
)



print(
    "Setores:",
    len(df)
)



# ============================================================
# CRITÉRIOS
# ============================================================


print("\nCriando indicadores...")


df["SUSPEITO_L_HAB_DIA"] = False


df.loc[
    df["L_HAB_DIA"] > 500,
    "SUSPEITO_L_HAB_DIA"
] = True



df["POP_BAIXA"] = False


df.loc[
    df["POPULACAO"] < 100,
    "POP_BAIXA"
] = True



df["CONSUMO_ALTO"] = False


df.loc[
    df["CONSUMO_MEDIO_MES"] >
    df["CONSUMO_MEDIO_MES"].quantile(0.99),
    "CONSUMO_ALTO"
] = True



# ============================================================
# CLASSIFICAÇÃO
# ============================================================


def classe(valor):

    if pd.isna(valor):
        return "Sem população"

    if valor <= 100:
        return "Baixo"

    if valor <= 200:
        return "Moderado"

    if valor <= 300:
        return "Elevado"

    return "Muito elevado"



df["CLASSE"] = df["L_HAB_DIA"].apply(classe)



# ============================================================
# EXPORTAR SUSPEITOS
# ============================================================


suspeitos = df[

    (

        df["SUSPEITO_L_HAB_DIA"]

    )

    |

    (

        df["POP_BAIXA"]

    )

    |

    (

        df["CONSUMO_ALTO"]

    )

].copy()



suspeitos = suspeitos.sort_values(

    "L_HAB_DIA",

    ascending=False

)



suspeitos.to_csv(

    os.path.join(

        PASTA,

        "setores_suspeitos_lhabdia.csv"

    ),

    index=False,

    encoding="utf-8-sig"

)



# ============================================================
# TOP 100
# ============================================================


top100 = (

    df

    .sort_values(

        "L_HAB_DIA",

        ascending=False

    )

    .head(100)

)



top100.to_csv(

    os.path.join(

        PASTA,

        "top_100_maiores_lhabdia.csv"

    ),

    index=False,

    encoding="utf-8-sig"

)



# ============================================================
# RESUMO
# ============================================================


resumo = (

    df["CLASSE"]

    .value_counts()

    .reset_index()

)



resumo.columns = [

    "CLASSE",

    "QUANTIDADE"

]



resumo.to_csv(

    os.path.join(

        PASTA,

        "resumo_classes_lhabdia.csv"

    ),

    index=False,

    encoding="utf-8-sig"

)



# ============================================================
# RESULTADO
# ============================================================


print("\n==============================")
print("RESULTADO")
print("==============================")


print(

    "Setores suspeitos:",

    len(suspeitos)

)


print(

    "\nTop 10 maiores:"

)


print(

    top100[

        [

            "CD_SETOR_FINAL",

            "POPULACAO",

            "MATRICULAS",

            "CONSUMO_MEDIO_MES",

            "L_HAB_DIA"

        ]

    ]

    .head(10)

)



print("\nArquivos gerados:")

print("- setores_suspeitos_lhabdia.csv")
print("- top_100_maiores_lhabdia.csv")
print("- resumo_classes_lhabdia.csv")


print(

    "\nTempo:",

    round(time.time()-inicio,2),

    "segundos"

)


print("\nFim Código 97.")