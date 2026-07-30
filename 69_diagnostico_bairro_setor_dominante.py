# ============================================================
# 69_diagnostico_bairro_setor_dominante.py
#
# Diagnóstico:
# BAIRRO -> SETOR DOMINANTE
#
# Mede potencial de recuperação probabilística.
# Não altera a base.
#
# ============================================================

import pandas as pd
import os
import unicodedata
import re
import time


inicio = time.time()


print("="*70)
print("DIAGNÓSTICO BAIRRO -> SETOR DOMINANTE")
print("="*70)



ARQUIVO = (
    "resultados/"
    "base_setor_final_CEP.csv"
)


SAIDA = (
    "resultados/"
    "diagnostico_bairro_setor_dominante.csv"
)



# ------------------------------------------------------------
# funções
# ------------------------------------------------------------

def normalizar(valor):

    if pd.isna(valor):

        return ""

    valor = str(valor).upper()


    valor = (
        unicodedata
        .normalize(
            "NFKD",
            valor
        )
        .encode(
            "ASCII",
            "ignore"
        )
        .decode(
            "ASCII"
        )
    )


    valor = re.sub(
        r"[^A-Z0-9 ]",
        " ",
        valor
    )


    valor = re.sub(
        r"\s+",
        " ",
        valor
    )


    return valor.strip()



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
# campo setor
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
# separar
# ------------------------------------------------------------

com = df[

    df[campo_setor].notna()

].copy()



sem = df[

    df[campo_setor].isna()

].copy()



print(
    "Com setor:",
    len(com)
)


print(
    "Sem setor:",
    len(sem)
)



# ------------------------------------------------------------
# normalização
# ------------------------------------------------------------

print("\nNormalizando bairros...")


com["BAIRRO_NORM"] = (

    com["Bairro"]

    .apply(normalizar)

)



sem["BAIRRO_NORM"] = (

    sem["Bairro"]

    .apply(normalizar)

)



# remover vazio

com = com[

    com["BAIRRO_NORM"] != ""

]


sem = sem[

    sem["BAIRRO_NORM"] != ""

]



# ------------------------------------------------------------
# criar distribuição bairro/setor
# ------------------------------------------------------------

print("\nCriando distribuição...")


dist = (

    com

    .groupby(

        [

            "BAIRRO_NORM",

            campo_setor

        ]

    )

    .size()

    .reset_index(

        name="quantidade"

    )

)



total_bairro = (

    dist

    .groupby(

        "BAIRRO_NORM"

    )

    ["quantidade"]

    .sum()

    .reset_index(

        name="total_bairro"

    )

)



dominante = (

    dist

    .sort_values(

        "quantidade",

        ascending=False

    )

    .drop_duplicates(

        "BAIRRO_NORM"

    )

)



dominante = dominante.merge(

    total_bairro,

    on="BAIRRO_NORM",

    how="left"

)



dominante["confianca"] = (

    dominante["quantidade"]

    /

    dominante["total_bairro"]

    *

    100

)



dominante = dominante.rename(

    columns={

        campo_setor:

        "SETOR_REGRA"

    }

)



print(

    "Bairros analisados:",

    len(dominante)

)



# ------------------------------------------------------------
# aplicar teste
# ------------------------------------------------------------

print("\nTestando bairros sem setor...")


teste = sem.merge(

    dominante[

        [

            "BAIRRO_NORM",

            "SETOR_REGRA",

            "confianca"

        ]

    ],

    on="BAIRRO_NORM",

    how="left"

)



if "SETOR_REGRA" not in teste.columns:

    teste["SETOR_REGRA"] = pd.NA


if "confianca" not in teste.columns:

    teste["confianca"] = pd.NA



# ------------------------------------------------------------
# resultado
# ------------------------------------------------------------

resultado = pd.DataFrame({

    "indicador":[

        "sem_setor_total",

        "bairro_com_referencia",

        "sem_referencia",

        "confianca_100",

        "confianca_maior_90",

        "confianca_maior_70",

        "confianca_maior_50"

    ],


    "quantidade":[

        len(sem),

        teste["SETOR_REGRA"].notna().sum(),

        teste["SETOR_REGRA"].isna().sum(),

        (teste["confianca"] == 100).sum(),

        (teste["confianca"] >= 90).sum(),

        (teste["confianca"] >= 70).sum(),

        (teste["confianca"] >= 50).sum()

    ]

})



# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

os.makedirs(

    "resultados",

    exist_ok=True

)



resultado.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)



print("\n")
print("="*70)
print("RESULTADO")
print("="*70)


print(resultado)



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