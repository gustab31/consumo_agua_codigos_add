# ============================================================
# 81_refinar_endereco_setor.py
#
# REFINAMENTO ENDEREÇO x SETOR CENSITÁRIO
#
# Entrada:
#   resultados/consumo_com_endereco.csv
#   joinville_setores_mapa.shp
#
# Saída:
#   resultados/consumo_setor_refinado.csv
#
# ============================================================


import os
import re
import time
import warnings
import unicodedata

import pandas as pd
import geopandas as gpd


warnings.filterwarnings("ignore")


inicio = time.time()


print("="*70)
print("REFINAMENTO ENDEREÇO x SETOR CENSITÁRIO")
print("="*70)



RESULTADOS = "resultados"


arquivo_consumo = os.path.join(
    RESULTADOS,
    "consumo_com_endereco.csv"
)


arquivo_shp = "joinville_setores_mapa.shp"



# ============================================================
# FUNÇÃO NORMALIZAÇÃO
# ============================================================


def normalizar(texto):

    if pd.isna(texto):

        return ""

    texto = str(texto).upper().strip()


    texto = unicodedata.normalize(
        "NFKD",
        texto
    )


    texto = "".join(
        c for c in texto
        if not unicodedata.combining(c)
    )


    texto = re.sub(
        r"\s+",
        " ",
        texto
    )


    return texto



# ============================================================
# EXTRAÇÃO
# ============================================================


def extrair_numero(texto):

    achou = re.search(
        r"\b\d+\b",
        texto
    )

    if achou:

        return achou.group()

    return ""



def extrair_logradouro(texto):

    achou = re.search(
        r"\b\d+\b",
        texto
    )

    if achou:

        return texto[:achou.start()].strip()

    return texto.strip()



# ============================================================
# LER CONSUMO
# ============================================================


print("\nLendo consumo...")


df = pd.read_csv(

    arquivo_consumo,

    encoding="utf-8-sig",

    low_memory=False

)



print(

    "Registros:",

    len(df)

)



df["BAIRRO_NORM"] = (

    df["Bairro"]

    .apply(normalizar)

)



df["ENDERECO_NORM"] = (

    df["Endereco"]

    .apply(normalizar)

)



df["LOGRADOURO"] = (

    df["ENDERECO_NORM"]

    .apply(extrair_logradouro)

)



df["NUMERO"] = (

    df["ENDERECO_NORM"]

    .apply(extrair_numero)

)



# ============================================================
# LER SHAPE
# ============================================================


print("\nLendo setores...")


gdf = gpd.read_file(

    arquivo_shp

)



print(

    "Setores:",

    len(gdf)

)



gdf["BAIRRO_NORM"] = (

    gdf["NM_BAIRRO"]

    .apply(normalizar)

)



# ============================================================
# PREPARAR ÍNDICE DE SETORES
# ============================================================


print("\nCriando índice...")


# Como o shapefile não possui ruas,
# usamos o bairro como unidade espacial
# e selecionamos setores únicos.


indice = (

    gdf

    [

        [

            "CD_SETOR",

            "BAIRRO_NORM"

        ]

    ]

    .drop_duplicates()

)



# quantidade de setores por bairro

qtd = (

    indice.groupby(

        "BAIRRO_NORM"

    )

    [

        "CD_SETOR"

    ]

    .nunique()

)



# ============================================================
# ASSOCIAÇÃO CONTROLADA
# ============================================================


print("\nAssociando...")


def escolher_setor(bairro):


    candidatos = indice[

        indice["BAIRRO_NORM"]

        == bairro

    ]["CD_SETOR"].tolist()


    if len(candidatos) == 1:

        return candidatos[0]


    return None



df["CD_SETOR"] = (

    df["BAIRRO_NORM"]

    .apply(escolher_setor)

)



# ============================================================
# CLASSIFICAÇÃO
# ============================================================


df["CONFIANCA_SETOR"] = "BAIXA"



df.loc[

    df["CD_SETOR"].notna(),

    "CONFIANCA_SETOR"

] = "ALTA"



df["TIPO_ASSOCIACAO"] = "MULTIPLO"



df.loc[

    df["CD_SETOR"].notna(),

    "TIPO_ASSOCIACAO"

] = "UNICO"



# ============================================================
# SALVAR
# ============================================================


saida = os.path.join(

    RESULTADOS,

    "consumo_setor_refinado.csv"

)



df.to_csv(

    saida,

    index=False,

    encoding="utf-8-sig"

)



print("\nResumo:")


print(

    df["TIPO_ASSOCIACAO"]

    .value_counts()

)



print(

    df["CONFIANCA_SETOR"]

    .value_counts()

)



print(

    "\nArquivo criado:",

    saida

)



print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim Código 81.")