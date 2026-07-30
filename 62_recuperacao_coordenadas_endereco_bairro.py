# ============================================================
# 62_recuperacao_coordenadas_endereco_bairro.py
#
# Recupera coordenadas usando:
# Endereco + Bairro
#
# ============================================================

import os
import time
import re
import unicodedata
import pandas as pd


inicio = time.time()


print("="*70)
print("RECUPERAÇÃO DE COORDENADAS POR ENDEREÇO + BAIRRO")
print("="*70)


BASE = (
    "resultados/"
    "base_setor_final_CEP.csv"
)

GEO = (
    "resultados/"
    "enderecos_geocodificados.csv"
)


SAIDA = (
    "resultados/"
    "base_com_coordenadas_recuperadas.csv"
)


RESUMO = (
    "resultados/"
    "resumo_recuperacao_coordenadas.csv"
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

print("\nLendo arquivos...")


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
    "Geocodificação:",
    len(geo)
)



# ------------------------------------------------------------
# criar chaves
# ------------------------------------------------------------

print("\nCriando chave endereço + bairro...")


for tabela in [df, geo]:

    tabela["END_NORM"] = (
        tabela["Endereco"]
        .apply(normalizar)
    )


    tabela["BAI_NORM"] = (
        tabela["Bairro"]
        .apply(normalizar)
    )



    tabela["CHAVE_END_BAIRRO"] = (

        tabela["END_NORM"]

        +

        "|"

        +

        tabela["BAI_NORM"]

    )



# ------------------------------------------------------------
# preparar geocodificação
# ------------------------------------------------------------

print("\nPreparando coordenadas...")


geo2 = geo[

    [

        "CHAVE_END_BAIRRO",

        "latitude",

        "longitude"

    ]

].copy()



geo2 = geo2.drop_duplicates(

    "CHAVE_END_BAIRRO"

)



print(

    "Chaves geocodificadas:",

    len(geo2)

)



# ------------------------------------------------------------
# merge
# ------------------------------------------------------------

print("\nAplicando ligação...")


df = df.merge(

    geo2,

    on="CHAVE_END_BAIRRO",

    how="left"

)



df["latitude"] = pd.to_numeric(

    df["latitude"],

    errors="coerce"

)


df["longitude"] = pd.to_numeric(

    df["longitude"],

    errors="coerce"

)



# ------------------------------------------------------------
# resumo
# ------------------------------------------------------------

com_coord = (

    df["latitude"]

    .notna()

    .sum()

)



sem_coord = (

    len(df)

    -

    com_coord

)



resumo = pd.DataFrame({

    "indicador":[

        "total_registros",

        "com_coordenada",

        "sem_coordenada",

        "percentual_cobertura"

    ],

    "valor":[

        len(df),

        com_coord,

        sem_coord,

        round(

            com_coord / len(df) * 100,

            2

        )

    ]

})



print("\n")
print("="*70)
print("RESULTADO")
print("="*70)


print(resumo)



# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

os.makedirs(

    "resultados",

    exist_ok=True

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