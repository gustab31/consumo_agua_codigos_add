# ============================================================
# 78_diagnostico_endereco_setores.py
#
# DIAGNÓSTICO:
#
# Endereço CAJ
#      |
#      |
#      ↓
# Setores censitários
#
# Analisa:
# - Bairro
# - CEP
# - Cobertura espacial
#
# ============================================================


import os
import time
import warnings

import pandas as pd
import geopandas as gpd


warnings.filterwarnings("ignore")


inicio = time.time()



print("="*70)
print("DIAGNÓSTICO ENDEREÇO x SETORES CENSITÁRIOS")
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



arquivo_shp = "joinville_setores_mapa.shp"



# ============================================================
# LER CONSUMO COM ENDEREÇO
# ============================================================


print("\nLendo consumo com endereço...")


df = pd.read_csv(

    arquivo_consumo,

    encoding="utf-8-sig",

    low_memory=False

)



print(

    "Linhas:",

    len(df)

)



print("\nColunas:")


for c in df.columns:

    print("-", c)



# ============================================================
# LIMPEZA
# ============================================================


for c in [

    "Bairro",

    "CEP",

    "Endereco",

    "Localizacao"

]:


    if c in df.columns:


        df[c] = (

            df[c]

            .astype(str)

            .str.strip()

            .str.upper()

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
# BAIRROS SHAPEFILE
# ============================================================


print("\nAnalisando bairros...")


col_bairro = None



for c in gdf.columns:


    if "BAIRRO" in c.upper():


        col_bairro = c

        break



if col_bairro is None:


    raise Exception(

        "Não encontrou bairro no shapefile"

    )



print(

    "Campo bairro shapefile:",

    col_bairro

)



bairros_setor = (

    gdf[col_bairro]

    .astype(str)

    .str.strip()

    .str.upper()

    .drop_duplicates()

)



print(

    "Bairros nos setores:",

    len(bairros_setor)

)



# ============================================================
# COMPARAR BAIRROS
# ============================================================


print("\nComparando bairros...")


df_bairros = (

    df["Bairro"]

    .dropna()

    .unique()

)



resultado_bairro = []



for b in df_bairros:


    resultado_bairro.append({

        "bairro": b,

        "existe_setor": b in set(bairros_setor)

    })



diag_bairro = pd.DataFrame(

    resultado_bairro

)



diag_bairro.to_excel(

    os.path.join(

        RESULTADOS,

        "diagnostico_bairros_endereco.xlsx"

    ),

    index=False

)



print(

    "\nBairros CAJ:",

    len(diag_bairro)

)



print(

    diag_bairro["existe_setor"]

    .value_counts()

)



# ============================================================
# DISTRIBUIÇÃO DE MATRÍCULAS POR BAIRRO
# ============================================================


bairro_consumo = (

    df.groupby("Bairro")

    .agg(

        matriculas=(

            "MATRICULA",

            "nunique"

        ),

        registros=(

            "MATRICULA",

            "count"

        )

    )

    .reset_index()

)



bairro_consumo.to_excel(

    os.path.join(

        RESULTADOS,

        "consumo_por_bairro.xlsx"

    ),

    index=False

)



# ============================================================
# CEP
# ============================================================


print("\nAnalisando CEP...")


if "CEP" in df.columns:


    cep = (

        df["CEP"]

        .value_counts()

        .reset_index()

    )


    cep.columns = [

        "CEP",

        "quantidade"

    ]


    cep.to_excel(

        os.path.join(

            RESULTADOS,

            "distribuicao_CEP.xlsx"

        ),

        index=False

    )


    print(

        "CEPs encontrados:",

        len(cep)

    )



# ============================================================
# SALVAR AMOSTRA
# ============================================================


df.sample(

    min(5000,len(df)),

    random_state=10

).to_excel(

    os.path.join(

        RESULTADOS,

        "amostra_enderecos_para_validacao.xlsx"

    ),

    index=False

)



print("\nArquivos gerados:")

print("- diagnostico_bairros_endereco.xlsx")

print("- consumo_por_bairro.xlsx")

print("- distribuicao_CEP.xlsx")

print("- amostra_enderecos_para_validacao.xlsx")



print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim Código 78.")