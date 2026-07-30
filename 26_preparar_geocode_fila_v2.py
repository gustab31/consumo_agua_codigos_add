# ============================================================
# 26_preparar_geocode_fila_v2.py
#
# Prepara endereços prioritários para geocodificação
#
# ============================================================


import pandas as pd
import os
import time
import re


inicio = time.time()


print("="*60)
print("PREPARANDO GEOCODIFICACAO FILA PRIORIDADE V2")
print("="*60)



ARQ_ENTRADA = (
    "resultados/"
    "fila_geocodificacao_prioridade_alta_v2.csv"
)


SAIDA = (
    "resultados/"
    "geocode_fila_prioridade_v2.csv"
)



# ============================================================
# LEITURA
# ============================================================


if not os.path.exists(ARQ_ENTRADA):

    raise FileNotFoundError(
        ARQ_ENTRADA
    )


print("\nLendo fila...")


df = pd.read_csv(

    ARQ_ENTRADA,

    low_memory=False

)


print(

    "Registros:",

    len(df)

)



# ============================================================
# LIMPEZA CEP
# ============================================================


print("\nTratando CEP...")


def limpar_cep(valor):

    if pd.isna(valor):

        return ""

    valor = str(valor)


    numeros = re.sub(

        r"\D",

        "",

        valor

    )


    if len(numeros) == 8:

        return (

            numeros[:5]

            +

            "-"

            +

            numeros[5:]

        )


    return ""



if "CEP" in df.columns:


    df["CEP_LIMPO"] = (

        df["CEP"]

        .apply(limpar_cep)

    )


else:

    df["CEP_LIMPO"] = ""



# ============================================================
# LIMPEZA TEXTO
# ============================================================


def limpar_texto(x):

    if pd.isna(x):

        return ""

    return (

        str(x)

        .upper()

        .strip()

    )



df["endereco"] = (

    df["endereco"]

    .apply(limpar_texto)

)


df["bairro"] = (

    df["bairro"]

    .apply(limpar_texto)

)



# ============================================================
# CRIAR CONSULTA
# ============================================================


print("\nCriando consultas...")


def montar_consulta(row):

    partes = [

        row["endereco"],

        row["bairro"],

        "JOINVILLE",

        "SC",

        "BRASIL"

    ]


    return ", ".join(

        [

            p

            for p in partes

            if p

        ]

    )



df["consulta"] = (

    df.apply(

        montar_consulta,

        axis=1

    )

)



# ============================================================
# REMOVER DUPLICADOS
# ============================================================


antes = len(df)



df = (

    df

    .drop_duplicates(

        subset=[

            "endereco",

            "bairro"

        ]

    )

)



print(

    "Duplicados removidos:",

    antes-len(df)

)



# ============================================================
# ORDENAR
# ============================================================


ordem = {

    "MUITO_ALTA":0,

    "ALTA":1,

    "MEDIA":2

}


df["ordem"] = (

    df["prioridade"]

    .map(ordem)

)



df = (

    df

    .sort_values(

        [

            "ordem",

            "total_matriculas"

        ],

        ascending=[

            True,

            False

        ]

    )

    .drop(

        columns=["ordem"]

    )

)



# ============================================================
# SALVAR
# ============================================================


df.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)



print("\n")

print("="*60)

print("RESULTADO")

print("="*60)


print(

    "Endereços preparados:",

    len(df)

)


print("\nAmostra:")

print(

    df[

        [

            "endereco",

            "bairro",

            "CEP_LIMPO",

            "total_matriculas",

            "prioridade",

            "consulta"

        ]

    ]

    .head(20)

)



print("\nArquivo:")

print(SAIDA)



print("\nTempo:")

print(

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)


print("\nFim.")