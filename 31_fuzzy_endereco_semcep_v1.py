# ============================================================
# 31_fuzzy_endereco_semcep_v1.py
#
# Recuperação CD_SETOR por fuzzy:
# logradouro + bairro
#
# ============================================================


import pandas as pd
import re
import unicodedata
import time
import os

from rapidfuzz import process, fuzz



inicio = time.time()


print("="*60)
print("FUZZY ENDEREÇO SEM CEP")
print("="*60)



ENTRADA = (
    "resultados/"
    "base_residencial_setor_fuzzy_v1.csv"
)


SAIDA = (
    "resultados/"
    "base_residencial_setor_fuzzy_semcep_v1.csv"
)


RESUMO = (
    "resultados/"
    "resumo_fuzzy_semcep_v1.csv"
)



# ============================================================
# LEITURA
# ============================================================


df = pd.read_csv(

    ENTRADA,

    low_memory=False

)


print("\nBase:")

print(df.shape)



if "CD_SETOR" not in df.columns:

    df["CD_SETOR"] = None



# ============================================================
# NORMALIZAÇÃO
# ============================================================


def normalizar(txt):

    if pd.isna(txt):

        return ""


    txt = str(txt).upper()


    txt = (

        unicodedata

        .normalize(

            "NFKD",

            txt

        )

        .encode(

            "ASCII",

            "ignore"

        )

        .decode()

    )


    txt = re.sub(

        r"\d+",

        "",

        txt

    )


    txt = re.sub(

        r"[^A-Z]",

        "",

        txt

    )


    return txt



# ============================================================
# CHAVES
# ============================================================


print("\nCriando chaves...")


df["RUA_FUZZY2"] = (

    df["Endereco"]

    .apply(normalizar)

)


df["BAIRRO_FUZZY2"] = (

    df["Bairro"]

    .apply(normalizar)

)



df["CHAVE_FUZZY2"] = (

    df["RUA_FUZZY2"]

    +

    "_"

    +

    df["BAIRRO_FUZZY2"]

)



# ============================================================
# REFERÊNCIA
# ============================================================


ref = df[

    df["CD_SETOR"]

    .notna()

].copy()



print(

    "Referências:",

    len(ref)

)



mapa = (

    ref

    .groupby(

        "CHAVE_FUZZY2"

    )["CD_SETOR"]

    .unique()

)



chaves = list(

    mapa.index

)



# ============================================================
# FUZZY
# ============================================================


print("\nExecutando comparação...")


novos = 0

cont = 0



for idx,row in df.iterrows():


    if pd.notna(row["CD_SETOR"]):

        continue



    chave = row["CHAVE_FUZZY2"]


    if len(chave) < 8:

        continue



    resultado = process.extractOne(

        chave,

        chaves,

        scorer=fuzz.ratio

    )



    if resultado is None:

        continue



    melhor, score, _ = resultado



    # critério mais rigoroso

    if score >= 92:


        setores = mapa[melhor]


        if len(setores) == 1:


            df.at[

                idx,

                "CD_SETOR"

            ] = setores[0]


            df.at[

                idx,

                "metodo_setor"

            ] = "fuzzy_semcep"



            novos += 1



    cont += 1


    if cont % 5000 == 0:

        print(

            "Processados:",

            cont

        )



# ============================================================
# RESUMO
# ============================================================


total = len(df)


com_setor = (

    df["CD_SETOR"]

    .notna()

    .sum()

)



resumo = pd.DataFrame({

    "indicador":[

        "total",

        "com_CD_SETOR",

        "sem_CD_SETOR",

        "novos_fuzzy_semcep",

        "percentual"

    ],

    "valor":[

        total,

        com_setor,

        total-com_setor,

        novos,

        round(

            com_setor /

            total *

            100,

            2

        )

    ]

})



# ============================================================
# SALVAR
# ============================================================


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



print("\n")

print("="*60)

print("RESULTADO")

print("="*60)


print(resumo)


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