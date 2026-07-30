# ============================================================
# 68_diagnostico_logradouro_bairro_normalizado.py
#
# Diagnóstico:
# LOGRADOURO NORMALIZADO + BAIRRO -> SETOR
#
# Não faz inferência.
# Mede potencial de recuperação.
#
# ============================================================

import pandas as pd
import os
import re
import unicodedata
import time


inicio = time.time()


print("="*70)
print("DIAGNÓSTICO LOGRADOURO + BAIRRO NORMALIZADO")
print("="*70)



ARQUIVO = (
    "resultados/"
    "base_setor_final_CEP.csv"
)


SAIDA = (
    "resultados/"
    "diagnostico_logradouro_bairro_normalizado.csv"
)



# ------------------------------------------------------------
# funções
# ------------------------------------------------------------

def limpar_texto(valor):

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
        r"\s+",
        " ",
        valor
    )


    return valor.strip()



def normalizar_logradouro(valor):

    valor = limpar_texto(valor)


    # remove número

    valor = re.sub(
        r"\s+\d+.*$",
        "",
        valor
    )


    substituicoes = {

        "RUA ": "R ",
        "AVENIDA ": "AV ",
        "ESTRADA ": "EST ",
        "RODOVIA ": "ROD ",
        "TRAVESSA ": "TRAV "

    }


    for antigo, novo in substituicoes.items():

        if valor.startswith(antigo):

            valor = valor.replace(
                antigo,
                novo,
                1
            )


    valor = re.sub(
        r"[^A-Z0-9 ]",
        "",
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
# normalização
# ------------------------------------------------------------

print("\nNormalizando campos...")


for tabela in [com, sem]:

    tabela["LOGRADOURO_NORM"] = (

        tabela["Endereco"]

        .apply(normalizar_logradouro)

    )


    tabela["BAIRRO_NORM"] = (

        tabela["Bairro"]

        .apply(limpar_texto)

    )



# ------------------------------------------------------------
# criar regras
# ------------------------------------------------------------

print("\nCriando regras...")


regras = (

    com

    .groupby(

        [

            "LOGRADOURO_NORM",

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

    regras

    .groupby(

        [

            "LOGRADOURO_NORM",

            "BAIRRO_NORM"

        ]

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

        [

            "LOGRADOURO_NORM",

            "BAIRRO_NORM"

        ]

    )

)



dominante = dominante.merge(

    totais,

    on=[

        "LOGRADOURO_NORM",

        "BAIRRO_NORM"

    ],

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

    "Regras criadas:",

    len(dominante)

)



# ------------------------------------------------------------
# teste
# ------------------------------------------------------------

print("\nTestando...")


teste = sem.merge(

    dominante[

        [

            "LOGRADOURO_NORM",

            "BAIRRO_NORM",

            "SETOR_REGRA",

            "confianca"

        ]

    ],

    on=[

        "LOGRADOURO_NORM",

        "BAIRRO_NORM"

    ],

    how="left"

)



# segurança

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

        "encontrou_logradouro_bairro",

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