# ============================================================
# 61_diagnostico_chave_geocodificacao.py
#
# Diagnóstico real de ligação da geocodificação
#
# Base:
# base_setor_final_CEP.csv
#
# Geo:
# enderecos_geocodificados.csv
#
# ============================================================

import os
import time
import re
import unicodedata
import pandas as pd


inicio = time.time()


print("="*70)
print("DIAGNÓSTICO DE CHAVE DE GEOCODIFICAÇÃO")
print("="*70)


BASE = "resultados/base_setor_final_CEP.csv"

GEO = "resultados/enderecos_geocodificados.csv"

SAIDA = (
    "resultados/"
    "diagnostico_chaves_geocodificacao.csv"
)



# ------------------------------------------------------------
# normalização
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
        r"[^A-Z0-9]",
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

print("\nLendo bases...")


df = pd.read_csv(
    BASE,
    low_memory=False
)


geo = pd.read_csv(
    GEO,
    low_memory=False
)



print(
    "Base:",
    len(df)
)


print(
    "Geo:",
    len(geo)
)



# ------------------------------------------------------------
# criar campos normalizados reais
# ------------------------------------------------------------

print("\nCriando campos normalizados...")


campos = [

    "Endereco",

    "Bairro",

    "CEP",

    "Endereco_Padronizado",

    "RUA_BASE",

    "BAIRRO_FUZZY",

    "CHAVE_FUZZY2"

]



for campo in campos:

    if campo in df.columns:

        df[campo+"_NORM"] = (

            df[campo]
            .apply(normalizar)

        )


    if campo in geo.columns:

        geo[campo+"_NORM"] = (

            geo[campo]
            .apply(normalizar)

        )



# ------------------------------------------------------------
# testes
# ------------------------------------------------------------

testes = [

    (
        "Endereco+Bairro+CEP",

        [
            "Endereco_NORM",
            "Bairro_NORM",
            "CEP_NORM"
        ]

    ),

    (
        "Endereco+Bairro",

        [
            "Endereco_NORM",
            "Bairro_NORM"
        ]

    ),

    (
        "Endereco+CEP",

        [
            "Endereco_NORM",
            "CEP_NORM"
        ]

    ),

    (
        "CEP+Bairro",

        [
            "CEP_NORM",
            "Bairro_NORM"
        ]

    ),

    (
        "Endereco_Padronizado",

        [
            "Endereco_Padronizado_NORM"
        ]

    ),

    (
        "CHAVE_FUZZY2+CEP",

        [
            "CHAVE_FUZZY2_NORM",
            "CEP_NORM"
        ]

    ),

    (
        "RUA_BASE+BAIRRO",

        [
            "RUA_BASE_NORM",
            "BAIRRO_FUZZY_NORM"
        ]

    )

]



resultados = []



print("\nTestando chaves...")



for nome, chave in testes:


    if not all(
        c in df.columns
        for c in chave
    ):

        continue



    if not all(
        c in geo.columns
        for c in chave
    ):

        continue



    print(
        "Testando:",
        nome
    )



    tabela_geo = geo[

        chave +

        [
            "latitude",
            "longitude"
        ]

    ].copy()



    tabela_geo = tabela_geo.drop_duplicates(
        chave
    )



    tabela_base = df[chave].drop_duplicates()



    ligado = tabela_base.merge(

        tabela_geo,

        on=chave,

        how="inner"

    )



    resultados.append({

        "chave": nome,

        "matches": len(ligado),

        "com_latitude":

            ligado["latitude"]
            .notna()
            .sum(),

        "percentual_base":

            round(

                len(ligado)
                /
                len(df)
                *
                100,

                2

            )

    })



# ------------------------------------------------------------
# resultado
# ------------------------------------------------------------

if len(resultados):

    resultado = pd.DataFrame(
        resultados
    )


    resultado = resultado.sort_values(

        "com_latitude",

        ascending=False

    )

else:

    resultado = pd.DataFrame({

        "chave":[],

        "matches":[],

        "com_latitude":[],

        "percentual_base":[]

    })



print("\n")
print("="*70)
print("RESULTADO")
print("="*70)


print(resultado)



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