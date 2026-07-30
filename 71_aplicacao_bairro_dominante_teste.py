# ============================================================
# 71_aplicacao_bairro_dominante_teste.py
#
# Teste:
# BAIRRO -> SETOR DOMINANTE
#
# Somente bairros com confianca >= 80%
#
# ============================================================

import pandas as pd
import os
import unicodedata
import re
import time


inicio = time.time()


print("="*70)
print("APLICAÇÃO TESTE - BAIRROS DOMINANTES")
print("="*70)



ARQUIVO = (
    "resultados/"
    "base_setor_final_CEP.csv"
)


PASTA = "resultados"



# ------------------------------------------------------------
# normalização
# ------------------------------------------------------------

def normalizar(valor):

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
# setor
# ------------------------------------------------------------

if "CD_SETOR_FINAL" in df.columns:

    campo_setor = "CD_SETOR_FINAL"

elif "CD_SETOR" in df.columns:

    campo_setor = "CD_SETOR"

else:

    raise Exception(
        "Campo setor não encontrado"
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
# bairro
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



com = com[
    com["BAIRRO_NORM"] != ""
]


sem = sem[
    sem["BAIRRO_NORM"] != ""
]



# ------------------------------------------------------------
# distribuição bairro/setor
# ------------------------------------------------------------

print("\nCalculando dominância...")


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



totais = (

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

    totais,

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



# bairros candidatos

candidatos = dominante[

    dominante["confianca"] >= 80

].copy()



print(
    "Bairros candidatos:",
    len(candidatos)
)



# ------------------------------------------------------------
# aplicação teste
# ------------------------------------------------------------

print("\nAplicando aos sem setor...")


teste = sem.merge(

    candidatos[

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
# classificação
# ------------------------------------------------------------

def classe(x):

    if pd.isna(x):
        return "SEM_INFERENCIA"

    if x >= 90:
        return "ALTA"

    if x >= 70:
        return "MEDIA"

    return "BAIXA"



teste["classe_confianca"] = (
    teste["confianca"]
    .apply(classe)
)



# ------------------------------------------------------------
# arquivos
# ------------------------------------------------------------

os.makedirs(
    PASTA,
    exist_ok=True
)



dominante.to_csv(

    PASTA +
    "/diagnostico_bairros_dominantes.csv",

    index=False,

    encoding="utf-8-sig"

)



teste.to_csv(

    PASTA +
    "/aplicacao_bairro_dominante_teste.csv",

    index=False,

    encoding="utf-8-sig"

)



resumo = pd.DataFrame({

    "indicador":[

        "bairros_analisados",

        "bairros_candidatos_80",

        "registros_sem_setor",

        "inferidos_teste",

        "confianca_alta",

        "confianca_media"

    ],

    "valor":[

        len(dominante),

        len(candidatos),

        len(sem),

        teste["SETOR_REGRA"].notna().sum(),

        (
            teste["classe_confianca"]
            ==
            "ALTA"
        ).sum(),

        (
            teste["classe_confianca"]
            ==
            "MEDIA"
        ).sum()

    ]

})



resumo.to_csv(

    PASTA +
    "/resumo_bairro_dominante.csv",

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
    "resultados/diagnostico_bairros_dominantes.csv"
)

print(
    "resultados/aplicacao_bairro_dominante_teste.csv"
)

print(
    "resultados/resumo_bairro_dominante.csv"
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