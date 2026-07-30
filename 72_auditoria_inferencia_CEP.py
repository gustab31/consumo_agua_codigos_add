# ============================================================
# 72_auditoria_inferencia_CEP.py
#
# Auditoria da regra:
# CEP -> CD_SETOR
#
# Avalia:
# - dominância do CEP
# - quantidade de setores por CEP
# - confiança
# - CEPs ambíguos
#
# ============================================================

import pandas as pd
import os
import time


inicio = time.time()


print("="*70)
print("AUDITORIA DA INFERÊNCIA POR CEP")
print("="*70)



ARQUIVO = (
    "resultados/"
    "base_setor_final_CEP.csv"
)


PASTA = "resultados"



# ------------------------------------------------------------
# leitura
# ------------------------------------------------------------

print("\nLendo base...")


df = pd.read_csv(

    ARQUIVO,

    low_memory=False

)



print(
    "Registros:",
    len(df)
)



# ------------------------------------------------------------
# identificar setor
# ------------------------------------------------------------

if "CD_SETOR_FINAL" in df.columns:

    campo_setor = "CD_SETOR_FINAL"

elif "CD_SETOR" in df.columns:

    campo_setor = "CD_SETOR"

else:

    raise Exception(
        "Campo de setor não encontrado"
    )



# ------------------------------------------------------------
# somente registros com setor
# ------------------------------------------------------------

df = df[

    df[campo_setor].notna()

].copy()



df = df[

    df["CEP"].notna()

].copy()



print(
    "Registros analisados:",
    len(df)
)



# ------------------------------------------------------------
# padronizar CEP
# ------------------------------------------------------------

print("\nNormalizando CEP...")


df["CEP_NORM"] = (

    df["CEP"]

    .astype(str)

    .str.replace(

        r"\D",

        "",

        regex=True

    )

)



df = df[

    df["CEP_NORM"] != ""

]



# ------------------------------------------------------------
# distribuição CEP/setor
# ------------------------------------------------------------

print("\nCalculando dominância...")


dist = (

    df

    .groupby(

        [

            "CEP_NORM",

            campo_setor

        ]

    )

    .size()

    .reset_index(

        name="quantidade"

    )

)



total = (

    dist

    .groupby(

        "CEP_NORM"

    )

    ["quantidade"]

    .sum()

    .reset_index(

        name="total_CEP"

    )

)



dist = dist.merge(

    total,

    on="CEP_NORM",

    how="left"

)



dist["percentual"] = (

    dist["quantidade"]

    /

    dist["total_CEP"]

    *

    100

)



# ------------------------------------------------------------
# setor dominante
# ------------------------------------------------------------

dominante = (

    dist

    .sort_values(

        "quantidade",

        ascending=False

    )

    .drop_duplicates(

        "CEP_NORM"

    )

)



dominante["classe"] = "BAIXA"


dominante.loc[

    dominante["percentual"] >= 95,

    "classe"

] = "ALTA"


dominante.loc[

    (

        dominante["percentual"] >= 80

    )

    &

    (

        dominante["percentual"] < 95

    ),

    "classe"

] = "MEDIA"



# ------------------------------------------------------------
# CEPs ambíguos
# ------------------------------------------------------------

n_setores = (

    dist

    .groupby(

        "CEP_NORM"

    )

    [campo_setor]

    .nunique()

    .reset_index(

        name="quantidade_setores"

    )

)



dominante = dominante.merge(

    n_setores,

    on="CEP_NORM",

    how="left"

)



ambiguos = dominante[

    dominante["quantidade_setores"] > 1

].copy()



# ------------------------------------------------------------
# resumo
# ------------------------------------------------------------

resumo = pd.DataFrame({

    "indicador":[

        "registros_analisados",

        "CEPs_modelados",

        "CEPs_alta_confianca",

        "CEPs_media_confianca",

        "CEPs_baixa_confianca",

        "CEPs_com_multiplos_setores",

        "maior_dominancia",

        "menor_dominancia"

    ],

    "valor":[

        len(df),

        len(dominante),

        (

            dominante["classe"]

            ==

            "ALTA"

        ).sum(),

        (

            dominante["classe"]

            ==

            "MEDIA"

        ).sum(),

        (

            dominante["classe"]

            ==

            "BAIXA"

        ).sum(),

        len(ambiguos),

        dominante["percentual"].max(),

        dominante["percentual"].min()

    ]

})



# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

os.makedirs(

    PASTA,

    exist_ok=True

)



dominante.to_csv(

    PASTA +

    "/auditoria_inferencia_CEP.csv",

    index=False,

    encoding="utf-8-sig"

)



ambiguos.to_csv(

    PASTA +

    "/CEPs_ambíguos.csv",

    index=False,

    encoding="utf-8-sig"

)



resumo.to_csv(

    PASTA +

    "/resumo_auditoria_CEP.csv",

    index=False,

    encoding="utf-8-sig"

)



print("\n")
print("="*70)
print("RESULTADO")
print("="*70)


print(resumo)



print("\nArquivos:")

print(
    "resultados/auditoria_inferencia_CEP.csv"
)

print(
    "resultados/CEPs_ambíguos.csv"
)

print(
    "resultados/resumo_auditoria_CEP.csv"
)



print("\nTempo:")

print(

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim.")