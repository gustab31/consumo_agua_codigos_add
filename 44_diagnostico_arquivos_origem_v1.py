# ============================================================
# 44_diagnostico_arquivos_origem_v1.py
#
# INVENTARIO DOS ARQUIVOS ORIGINAIS
#
# ============================================================


import os
import pandas as pd
import geopandas as gpd
import time


inicio = time.time()


print("="*70)
print("DIAGNOSTICO ARQUIVOS ORIGEM")
print("="*70)



PASTA = "."


saida = "diagnostico_arquivos_origem_v1.csv"


saida_colunas = "diagnostico_colunas_origem_v1.csv"



arquivos=[]


for arq in os.listdir(PASTA):

    if arq.lower().endswith(

        (

            ".csv",
            ".xlsx",
            ".xls",
            ".shp"

        )

    ):

        arquivos.append(arq)



print("\nArquivos encontrados:")

for a in arquivos:

    print("-",a)



resultado=[]

colunas=[]



for arquivo in arquivos:


    caminho=os.path.join(

        PASTA,

        arquivo

    )


    print("\n")

    print("="*60)

    print("Lendo:",arquivo)

    print("="*60)



    try:


        if arquivo.lower().endswith(".csv"):


            df=pd.read_csv(

                caminho,

                low_memory=False,

                nrows=5

            )


            tamanho=pd.read_csv(

                caminho,

                low_memory=False

            ).shape



            linhas=tamanho[0]



        elif arquivo.lower().endswith(

            (".xlsx",".xls")

        ):


            df=pd.read_excel(

                caminho,

                nrows=5

            )


            tamanho=pd.read_excel(

                caminho

            ).shape


            linhas=tamanho[0]



        elif arquivo.lower().endswith(".shp"):


            gdf=gpd.read_file(

                caminho

            )


            df=gdf.head()

            linhas=len(gdf)



        else:

            continue



        print(

            "Linhas:",

            linhas

        )


        print(

            "Colunas:",

            list(df.columns)

        )



        resultado.append({

            "arquivo":arquivo,

            "linhas":linhas,

            "colunas":len(df.columns)

        })



        for c in df.columns:


            colunas.append({

                "arquivo":arquivo,

                "coluna":c

            })



    except Exception as e:


        print(

            "ERRO:",

            e

        )


        resultado.append({

            "arquivo":arquivo,

            "linhas":"ERRO",

            "colunas":"ERRO"

        })



pd.DataFrame(resultado).to_csv(

    saida,

    index=False,

    encoding="utf-8-sig"

)


pd.DataFrame(colunas).to_csv(

    saida_colunas,

    index=False,

    encoding="utf-8-sig"

)



print("\n")

print("="*70)

print("FINAL")

print("="*70)


print("\nArquivos gerados:")

print(saida)

print(saida_colunas)


print("\nTempo:")

print(

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)


print("\nFim.")