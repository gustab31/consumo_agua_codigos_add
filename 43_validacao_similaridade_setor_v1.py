# ============================================================
# 43_validacao_similaridade_setor_v1.py
#
# VALIDACAO DOS CANDIDATOS DE SIMILARIDADE
#
# ============================================================


import pandas as pd
import time


inicio = time.time()


print("="*60)
print("VALIDACAO SIMILARIDADE SETOR - V1")
print("="*60)



ENTRADA = (
    "resultados/"
    "analise_similaridade_setor_v2.csv"
)


SAIDA = (
    "resultados/"
    "validacao_similaridade_setor_v1.csv"
)


RESUMO = (
    "resultados/"
    "resumo_validacao_similaridade_v1.csv"
)



print("\nLendo candidatos...")


df = pd.read_csv(

    ENTRADA,

    low_memory=False

)



print(

    "Candidatos:",

    len(df)

)



# ============================================================
# CLASSIFICACAO
# ============================================================


print("\nClassificando confiança...")


def classificar(x):

    if x >= 0.95:

        return "ALTA_CONFIANCA"

    elif x >= 0.90:

        return "MEDIA_CONFIANCA"

    else:

        return "REJEITAR"



df["confianca"] = (

    df["similaridade"]

    .apply(classificar)

)



# ============================================================
# CONFLITOS
# ============================================================


print("\nVerificando conflitos...")


conflitos = (

    df

    .groupby(

        "Endereco"

    )

    ["CD_SETOR_PROP"]

    .nunique()

    .reset_index()

)



conflitos = conflitos[

    conflitos["CD_SETOR_PROP"] > 1

]



df["conflito_endereco"] = (

    df["Endereco"]

    .isin(

        conflitos["Endereco"]

    )

)



# conflitos perdem confiança

df.loc[

    df["conflito_endereco"],

    "confianca"

] = "CONFLITO"



# ============================================================
# RESULTADO
# ============================================================


resumo = pd.DataFrame({

    "indicador":[

        "total_candidatos",

        "alta_confianca",

        "media_confianca",

        "conflitos"

    ],

    "valor":[

        len(df),

        (df["confianca"]=="ALTA_CONFIANCA").sum(),

        (df["confianca"]=="MEDIA_CONFIANCA").sum(),

        (df["confianca"]=="CONFLITO").sum()

    ]

})



print("\n")

print("="*60)

print("RESULTADO")

print("="*60)

print(resumo)



print("\nAmostra alta confiança:")


print(

    df[

        df["confianca"]

        =="ALTA_CONFIANCA"

    ]

    .head(30)

)



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