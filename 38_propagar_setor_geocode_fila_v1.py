# ============================================================
# 38_propagar_setor_geocode_fila_v1.py
#
# PROPAGA CD_SETOR CONFIRMADO POR GEOCODIFICAÇÃO
#
# ============================================================


import pandas as pd
import numpy as np
import unicodedata
import time
import os


inicio = time.time()


print("="*60)
print("PROPAGAÇÃO CD_SETOR - GEOCODE FILA V1")
print("="*60)



# ============================================================
# ARQUIVOS
# ============================================================


BASE = (
    "resultados/"
    "base_residencial_setor_logradouro_dominante_v1.csv"
)


GEOCODE = (
    "resultados/"
    "geocode_fila_com_CD_SETOR_v2.csv"
)


SAIDA = (
    "resultados/"
    "base_residencial_setor_geocode_fila_v1.csv"
)


RESUMO = (
    "resultados/"
    "resumo_geocode_fila_propagacao_v1.csv"
)



# ============================================================
# FUNÇÃO NORMALIZAÇÃO
# ============================================================


def normalizar(x):

    if pd.isna(x):

        return ""


    x = str(x).upper().strip()


    x = unicodedata.normalize(

        "NFKD",

        x

    ).encode(

        "ASCII",

        "ignore"

    ).decode(

        "ASCII"

    )


    x = (

        x.replace("  "," ")

        .replace("SN","SN")

    )


    return x



# ============================================================
# LER BASE
# ============================================================


print("\nLendo base...")


df = pd.read_csv(

    BASE,

    low_memory=False

)


print(

    "Base:",

    df.shape

)



# ============================================================
# IDENTIFICAR COLUNAS
# ============================================================


def achar_coluna(df, nomes):


    for n in nomes:

        if n in df.columns:

            return n


    raise Exception(

        f"Coluna não encontrada: {nomes}"

    )



col_end = achar_coluna(

    df,

    [

        "endereco",

        "Endereco"

    ]

)


col_bairro = achar_coluna(

    df,

    [

        "bairro",

        "Bairro"

    ]

)



# CD_SETOR

if "CD_SETOR" not in df.columns:


    df["CD_SETOR"] = np.nan



antes = df["CD_SETOR"].notna().sum()



print(

    "Com setor antes:",

    antes

)



# ============================================================
# LER GEOCODE
# ============================================================


print("\nLendo geocode...")


geo = pd.read_csv(

    GEOCODE,

    low_memory=False

)



print(

    "Registros geocode:",

    len(geo)

)



# ============================================================
# CHAVES
# ============================================================


print("\nCriando chaves...")


geo_end = achar_coluna(

    geo,

    [

        "endereco",

        "Endereco"

    ]

)


geo_bairro = achar_coluna(

    geo,

    [

        "bairro",

        "Bairro"

    ]

)



df["chave"] = (

    df[col_end].apply(normalizar)

    +

    "|"

    +

    df[col_bairro].apply(normalizar)

)



geo["chave"] = (

    geo[geo_end].apply(normalizar)

    +

    "|"

    +

    geo[geo_bairro].apply(normalizar)

)



# somente setores válidos

geo = geo[

    geo["CD_SETOR"].notna()

].copy()



mapa = (

    geo

    [["chave","CD_SETOR"]]

    .drop_duplicates()

)



print(

    "Endereços com setor:",

    len(mapa)

)



# ============================================================
# TRANSFERÊNCIA
# ============================================================


print("\nTransferindo setores...")


df = df.merge(

    mapa,

    on="chave",

    how="left",

    suffixes=("","_novo")

)



novo = (

    df["CD_SETOR_novo"].notna()

    &

    df["CD_SETOR"].isna()

)



df.loc[

    novo,

    "CD_SETOR"

] = df.loc[

    novo,

    "CD_SETOR_novo"

]



df["metodo_setor"] = df.get(

    "metodo_setor",

    ""

)



df["confianca"] = df.get(

    "confianca",

    ""

)



df.loc[

    novo,

    "metodo_setor"

] = "geocode_spatial_fila"



df.loc[

    novo,

    "confianca"

] = "ALTA"



df.drop(

    columns=["CD_SETOR_novo"],

    inplace=True,

    errors="ignore"

)



# ============================================================
# RESULTADO
# ============================================================


depois = df["CD_SETOR"].notna().sum()



resumo = pd.DataFrame({

    "indicador":[

        "total_registros",

        "com_CD_SETOR_antes",

        "novos_geocode_fila",

        "com_CD_SETOR_depois",

        "sem_CD_SETOR",

        "percentual"

    ],

    "valor":[

        len(df),

        antes,

        novo.sum(),

        depois,

        len(df)-depois,

        round(

            depois/len(df)*100,

            2

        )

    ]

})



print("\n")

print("="*60)

print("RESULTADO")

print("="*60)

print(resumo)



# ============================================================
# SALVAR
# ============================================================


print("\nSalvando...")


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