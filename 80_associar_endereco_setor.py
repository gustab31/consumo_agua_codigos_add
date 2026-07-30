# ============================================================
# 80_associar_endereco_setor.py
#
# ASSOCIAÇÃO ENDEREÇO CAJ x SETOR CENSITÁRIO
#
# Entrada:
#   resultados/consumo_com_endereco.csv
#   joinville_setores_mapa.shp
#
# Saída:
#   resultados/associacao_endereco_setor.csv
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
print("ASSOCIAÇÃO ENDEREÇO x SETOR CENSITÁRIO")
print("="*70)



RESULTADOS = "resultados"


arquivo_consumo = os.path.join(
    RESULTADOS,
    "consumo_com_endereco.csv"
)


arquivo_shp = "joinville_setores_mapa.shp"



# ============================================================
# NORMALIZA TEXTO
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
# EXTRAÇÃO ENDEREÇO
# ============================================================


def extrair_numero(endereco):

    achou = re.search(
        r"\b\d+\b",
        endereco
    )

    if achou:

        return achou.group()

    return ""



def extrair_logradouro(endereco):

    achou = re.search(
        r"\b\d+\b",
        endereco
    )

    if achou:

        return endereco[:achou.start()].strip()

    return endereco.strip()



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



print("\nSeparando endereço...")


df["NUMERO"] = (

    df["ENDERECO_NORM"]

    .apply(extrair_numero)

)



df["LOGRADOURO"] = (

    df["ENDERECO_NORM"]

    .apply(extrair_logradouro)

)



df["CHAVE_ENDERECO"] = (

    df["BAIRRO_NORM"]

    + "|"

    + df["LOGRADOURO"]

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



setores = gdf[

    [

        "CD_SETOR",

        "BAIRRO_NORM"

    ]

].copy()



# ============================================================
# CRUZAMENTO POR BAIRRO
# ============================================================


print("\nAssociando setores candidatos...")


df2 = df.merge(

    setores,

    on="BAIRRO_NORM",

    how="left",

    indicator=True

)



df2.rename(

    columns={

        "CD_SETOR":

        "CD_SETOR_CANDIDATO"

    },

    inplace=True

)



print(

    df2["_merge"]

    .value_counts()

)



# ============================================================
# CONTAR AMBIGUIDADE
# ============================================================


print("\nCalculando ambiguidade...")


controle = (

    df2.groupby(

        "CHAVE_ENDERECO"

    )

    [

        "CD_SETOR_CANDIDATO"

    ]

    .nunique()

    .reset_index()

)



controle.columns = [

    "CHAVE_ENDERECO",

    "QTD_SETORES"

]



df2 = df2.merge(

    controle,

    on="CHAVE_ENDERECO",

    how="left"

)



df2["TIPO_ASSOCIACAO"] = "MULTIPLO"



df2.loc[

    df2["QTD_SETORES"] == 1,

    "TIPO_ASSOCIACAO"

] = "UNICO"



df2.loc[

    df2["CD_SETOR_CANDIDATO"].isna(),

    "TIPO_ASSOCIACAO"

] = "SEM_SETOR"



# ============================================================
# SALVAR
# ============================================================


saida = os.path.join(

    RESULTADOS,

    "associacao_endereco_setor.csv"

)



df2.to_csv(

    saida,

    index=False,

    encoding="utf-8-sig"

)



print("\nResumo associação:")


print(

    df2["TIPO_ASSOCIACAO"]

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



print("\nFim Código 80.")