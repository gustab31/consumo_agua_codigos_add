# ============================================================
# 96_auditoria_lhabdia_setores.py
#
# AUDITORIA FINAL CONSUMO L/hab/dia
#
# Entrada:
#   resultados_04/consumo_lhabdia_setores.csv
#
# Saídas:
#   resultados_04/auditoria_lhabdia.csv
#   resultados_04/top_maiores_lhabdia.csv
#   resultados_04/top_menores_lhabdia.csv
#   resultados_04/setores_sem_populacao.csv
#
# ============================================================


import os
import time
import pandas as pd


inicio = time.time()


print("="*70)
print("AUDITORIA CONSUMO L/hab/dia")
print("="*70)



PASTA = "resultados_04"


arquivo = os.path.join(
    PASTA,
    "consumo_lhabdia_setores.csv"
)



# ============================================================
# LER
# ============================================================


print("\nLendo arquivo final...")


df = pd.read_csv(

    arquivo,

    encoding="utf-8-sig",

    low_memory=False

)



print(

    "Registros:",

    len(df)

)


print("\nColunas:")

for c in df.columns:

    print("-", c)



# ============================================================
# CLASSIFICAÇÃO
# ============================================================


print("\nClassificando consumo...")


def classe(valor):

    if pd.isna(valor):

        return "Sem população"

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



df["CLASSE_L_HAB_DIA"] = (

    df["L_HAB_DIA"]

    .apply(classe)

)



# ============================================================
# RESUMO
# ============================================================


print("\nDistribuição:")


print(

    df["CLASSE_L_HAB_DIA"]

    .value_counts()

)



print("\nEstatística:")


print(

    df["L_HAB_DIA"]

    .describe()

)



# ============================================================
# EXPORTAR AUDITORIA
# ============================================================


saida = os.path.join(

    PASTA,

    "auditoria_lhabdia.csv"

)


df.to_csv(

    saida,

    index=False,

    encoding="utf-8-sig"

)



# ============================================================
# MAIORES
# ============================================================


maiores = (

    df

    .sort_values(

        "L_HAB_DIA",

        ascending=False

    )

    .head(20)

)



maiores.to_csv(

    os.path.join(

        PASTA,

        "top_maiores_lhabdia.csv"

    ),

    index=False,

    encoding="utf-8-sig"

)



# ============================================================
# MENORES
# ============================================================


menores = (

    df

    .dropna(

        subset=["L_HAB_DIA"]

    )

    .sort_values(

        "L_HAB_DIA"

    )

    .head(20)

)



menores.to_csv(

    os.path.join(

        PASTA,

        "top_menores_lhabdia.csv"

    ),

    index=False,

    encoding="utf-8-sig"

)



# ============================================================
# SEM POPULAÇÃO
# ============================================================


sem_pop = df[

    df["POPULACAO"]

    .isna()

]


sem_pop.to_csv(

    os.path.join(

        PASTA,

        "setores_sem_populacao.csv"

    ),

    index=False,

    encoding="utf-8-sig"

)



# ============================================================
# IMPRESSÃO FINAL
# ============================================================


print("\n==============================")
print("ARQUIVOS GERADOS")
print("==============================")


print(
    "- auditoria_lhabdia.csv"
)

print(
    "- top_maiores_lhabdia.csv"
)

print(
    "- top_menores_lhabdia.csv"
)

print(
    "- setores_sem_populacao.csv"
)



print("\nResumo final:")


print(

    "Setores:",

    len(df)

)


print(

    "Sem população:",

    len(sem_pop)

)



print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim Código 96.")