# ============================================================
# 23_validar_malha_setores.py
#
# Objetivo:
# Encontrar qual shapefile possui CD_SETOR
# ============================================================


import geopandas as gpd
import os


print("="*60)
print("VALIDANDO MALHAS SHP")
print("="*60)



arquivos = [

    "Joinville_setores.shp",

    "joinville_setores_mapa.shp",

    "resultados_02/joinville_setores_mapa.shp",

    "resultados_02/joinville_consumo_p99_censitario_novo.shp",

    "resultados_03/joinville_setores_mapa.shp",

    "resultados_03/setores_sem_consumo.shp",

    "resultados_02/setores_consumo_final.shp",

    "resultados_02/setores_consumo_p99.shp",

    "resultados_02/setores_consumo_p99_final.shp"

]



resultado = []



for arquivo in arquivos:


    print("\n--------------------------------")

    print(arquivo)


    if not os.path.exists(arquivo):

        print("NÃO ENCONTRADO")

        continue


    try:

        gdf = gpd.read_file(

            arquivo

        )


        print(

            "Linhas:",

            len(gdf)

        )


        colunas = gdf.columns.tolist()


        print(

            "Tem CD_SETOR:",

            "CD_SETOR" in colunas

        )


        print(

            "Primeiras colunas:"

        )

        print(

            colunas[:15]

        )


        resultado.append({

            "arquivo": arquivo,

            "linhas": len(gdf),

            "CD_SETOR":

            "CD_SETOR" in colunas,

            "colunas":

            ";".join(colunas)

        })


    except Exception as e:


        print(

            "ERRO:",

            e

        )



print("\n")

print("="*60)

print("RESUMO")

print("="*60)



for r in resultado:

    print()

    print(

        r["arquivo"]

    )

    print(

        "Linhas:",

        r["linhas"]

    )

    print(

        "CD_SETOR:",

        r["CD_SETOR"]

    )



print("\nFim.")