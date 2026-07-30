# ============================================================
# 78_1_diagnostico_bairro_corrigido.py
#
# DIAGNÓSTICO:
#
# Endereço CAJ
#       |
#       | Bairro
#       ↓
# Setores censitários possíveis
#
# ============================================================


import os
import time
import warnings
import unicodedata

import pandas as pd
import geopandas as gpd


warnings.filterwarnings("ignore")


inicio = time.time()



print("="*70)
print("DIAGNÓSTICO BAIRRO x SETORES (CORRIGIDO)")
print("="*70)



# ============================================================
# CONFIGURAÇÃO
# ============================================================


RESULTADOS = "resultados"


os.makedirs(

    RESULTADOS,

    exist_ok=True

)



arquivo_consumo = os.path.join(

    RESULTADOS,

    "consumo_com_endereco.csv"

)


arquivo_shp = (

    "joinville_setores_mapa.shp"

)



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


    return texto



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

    "Linhas:",

    len(df)

)



if "Bairro" not in df.columns:


    raise Exception(

        "Campo Bairro não encontrado."

    )



df["BAIRRO_NORM"] = (

    df["Bairro"]

    .apply(normalizar)

)



print(

    "Bairros consumo:",

    df["BAIRRO_NORM"]

    .nunique()

)



# ============================================================
# LER SHAPEFILE
# ============================================================


print("\nLendo setores...")


gdf = gpd.read_file(

    arquivo_shp

)



print(

    "Setores:",

    len(gdf)

)



# ============================================================
# IDENTIFICAR NOME BAIRRO
# ============================================================


col_bairro = None



for c in gdf.columns:


    if c.upper() == "NM_BAIRRO":

        col_bairro = c

        break



if col_bairro is None:


    for c in gdf.columns:


        if "BAIRRO" in c.upper():


            col_bairro = c

            break




if col_bairro is None:


    raise Exception(

        "Não encontrou NM_BAIRRO."

    )



print(

    "Campo bairro:",

    col_bairro

)



gdf["BAIRRO_NORM"] = (

    gdf[col_bairro]

    .apply(normalizar)

)



# ============================================================
# COMPARAÇÃO
# ============================================================


print("\nComparando bairros...")


bairros_caj = (

    df["BAIRRO_NORM"]

    .drop_duplicates()

)



bairros_ibge = (

    gdf["BAIRRO_NORM"]

    .drop_duplicates()

)



comparacao = pd.DataFrame({

    "BAIRRO": bairros_caj

})



comparacao["EXISTE_SETOR"] = (

    comparacao["BAIRRO"]

    .isin(

        set(bairros_ibge)

    )

)



print(

    comparacao["EXISTE_SETOR"]

    .value_counts()

)



comparacao.to_excel(

    os.path.join(

        RESULTADOS,

        "comparacao_bairros_corrigida.xlsx"

    ),

    index=False

)



# ============================================================
# RELAÇÃO BAIRRO → SETORES
# ============================================================


print("\nCriando relação bairro-setor...")


relacao = gdf[

    [

        "CD_SETOR",

        col_bairro

    ]

].copy()



relacao["BAIRRO_NORM"] = (

    relacao[col_bairro]

    .apply(normalizar)

)



relacao = relacao[

    [

        "CD_SETOR",

        "BAIRRO_NORM"

    ]

]



relacao.to_excel(

    os.path.join(

        RESULTADOS,

        "bairro_para_setores.xlsx"

    ),

    index=False

)



# ============================================================
# QUANTIDADE DE SETORES POR BAIRRO
# ============================================================


resumo = (

    relacao

    .groupby(

        "BAIRRO_NORM"

    )

    .agg(

        setores=(

            "CD_SETOR",

            "count"

        )

    )

    .reset_index()

)



resumo.to_excel(

    os.path.join(

        RESULTADOS,

        "quantidade_setores_por_bairro.xlsx"

    ),

    index=False

)



print("\nArquivos gerados:")

print("- comparacao_bairros_corrigida.xlsx")

print("- bairro_para_setores.xlsx")

print("- quantidade_setores_por_bairro.xlsx")



print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim Código 78.1")