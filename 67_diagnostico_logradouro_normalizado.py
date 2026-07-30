# ============================================================
# 67_diagnostico_logradouro_normalizado_v3.py
# ============================================================

import pandas as pd
import os
import re
import unicodedata
import time


inicio = time.time()


print("="*70)
print("DIAGNÓSTICO POR LOGRADOURO NORMALIZADO")
print("="*70)



ARQUIVO = "resultados/base_setor_final_CEP.csv"

SAIDA = "resultados/diagnostico_logradouro_normalizado.csv"



def limpar_texto(valor):

    if pd.isna(valor):
        return ""

    valor = str(valor).upper()

    valor = (
        unicodedata
        .normalize("NFKD", valor)
        .encode("ASCII", "ignore")
        .decode("ASCII")
    )

    valor = re.sub(
        r"\s+",
        " ",
        valor
    )

    return valor.strip()



def normalizar_logradouro(valor):

    valor = limpar_texto(valor)

    valor = re.sub(
        r"\s+\d+.*$",
        "",
        valor
    )

    for a,b in {

        "RUA ":"R ",
        "AVENIDA ":"AV ",
        "ESTRADA ":"EST ",
        "RODOVIA ":"ROD ",
        "TRAVESSA ":"TRAV "

    }.items():

        if valor.startswith(a):

            valor = valor.replace(
                a,
                b,
                1
            )


    valor = re.sub(
        r"[^A-Z0-9 ]",
        "",
        valor
    )

    return re.sub(
        r"\s+",
        " ",
        valor
    ).strip()



print("\nLendo base...")


df = pd.read_csv(
    ARQUIVO,
    low_memory=False
)


if "CD_SETOR_FINAL" in df.columns:

    campo_setor = "CD_SETOR_FINAL"

elif "CD_SETOR" in df.columns:

    campo_setor = "CD_SETOR"

else:

    raise Exception(
        "Campo setor não encontrado"
    )



com = df[
    df[campo_setor].notna()
].copy()


sem = df[
    df[campo_setor].isna()
].copy()



print("Registros:",len(df))
print("Com setor:",len(com))
print("Sem setor:",len(sem))



print("\nNormalizando...")


com["LOGRADOURO_NORM"] = (
    com["Endereco"]
    .apply(normalizar_logradouro)
)


sem["LOGRADOURO_NORM"] = (
    sem["Endereco"]
    .apply(normalizar_logradouro)
)



com = com[
    com["LOGRADOURO_NORM"] != ""
]


sem = sem[
    sem["LOGRADOURO_NORM"] != ""
]



print("\nCriando regras...")


regras = (

    com

    .groupby(
        [
            "LOGRADOURO_NORM",
            campo_setor
        ]
    )

    .size()

    .reset_index(
        name="quantidade"
    )

)



if len(regras) == 0:

    raise Exception(
        "Nenhuma regra criada"
    )



totais = (

    regras

    .groupby(
        "LOGRADOURO_NORM"
    )

    ["quantidade"]

    .sum()

    .reset_index(
        name="total"
    )

)



dominante = (

    regras

    .sort_values(
        "quantidade",
        ascending=False
    )

    .drop_duplicates(
        "LOGRADOURO_NORM"
    )

)



dominante = dominante.merge(

    totais,

    on="LOGRADOURO_NORM",

    how="left"

)



dominante["confianca"] = (

    dominante["quantidade"]

    /

    dominante["total"]

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
    "Regras:",
    len(dominante)
)



print("\nTestando...")


teste = sem.merge(

    dominante[

        [
            "LOGRADOURO_NORM",
            "SETOR_REGRA",
            "confianca"

        ]

    ],

    on="LOGRADOURO_NORM",

    how="left"

)



# segurança

if "confianca" not in teste.columns:

    teste["confianca"] = pd.NA


if "SETOR_REGRA" not in teste.columns:

    teste["SETOR_REGRA"] = pd.NA



resultado = pd.DataFrame({

    "indicador":[

        "sem_setor_total",

        "encontrou_logradouro",

        "sem_referencia",

        "confianca_100",

        "confianca_maior_90",

        "confianca_maior_70"

    ],

    "quantidade":[

        len(sem),

        teste["SETOR_REGRA"].notna().sum(),

        teste["SETOR_REGRA"].isna().sum(),

        (teste["confianca"] == 100).sum(),

        (teste["confianca"] >= 90).sum(),

        (teste["confianca"] >= 70).sum()

    ]

})



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
print(round(time.time()-inicio,2),"segundos")


print("\nFim.")