# ============================================================
# 27_geocode_fila_prioridade_v2.py
#
# Geocodifica fila de endereços prioritários V2
#
# ============================================================


import pandas as pd
import requests
import time
import os


inicio = time.time()


print("="*60)
print("GEOCODIFICANDO FILA PRIORIDADE V2")
print("="*60)



ARQ_ENTRADA = (
    "resultados/"
    "geocode_fila_prioridade_v2.csv"
)


SAIDA = (
    "resultados/"
    "geocode_fila_prioridade_v2_resultado.csv"
)



# ============================================================
# LEITURA
# ============================================================


if not os.path.exists(ARQ_ENTRADA):

    raise FileNotFoundError(
        ARQ_ENTRADA
    )



df = pd.read_csv(

    ARQ_ENTRADA,

    low_memory=False

)



print("\nRegistros:")

print(len(df))



# ============================================================
# PREPARAR COLUNAS
# ============================================================


for c in [

    "status_geocode",
    "latitude",
    "longitude",
    "CD_SETOR",
    "metodo_setor",
    "confianca",
    "erro"

]:

    if c not in df.columns:

        df[c] = None



# ============================================================
# GEOCODIFICADOR
# ============================================================


def geocode(endereco):


    url = (

        "https://nominatim.openstreetmap.org/search"

    )


    params = {

        "q": endereco,

        "format": "json",

        "limit": 1,

        "countrycodes": "br"

    }


    headers = {

        "User-Agent":

        "pesquisa-censitario-agua"

    }



    try:


        r = requests.get(

            url,

            params=params,

            headers=headers,

            timeout=20

        )



        dados = r.json()



        if len(dados) > 0:


            return {

                "status":

                "encontrado",


                "latitude":

                float(

                    dados[0]["lat"]

                ),


                "longitude":

                float(

                    dados[0]["lon"]

                )

            }



        else:


            return {

                "status":

                "nao_encontrado"

            }



    except Exception as e:


        return {

            "status":

            "erro",


            "erro":

            str(e)

        }



# ============================================================
# PROCESSAMENTO
# ============================================================


print("\nIniciando...")


for i,row in df.iterrows():


    consulta = row["consulta"]


    print(

        f"{i+1}/{len(df)} - {consulta}"

    )



    resultado = geocode(

        consulta

    )



    df.loc[i,"status_geocode"] = (

        resultado.get(

            "status"

        )

    )


    if "latitude" in resultado:


        df.loc[i,"latitude"] = (

            resultado["latitude"]

        )


        df.loc[i,"longitude"] = (

            resultado["longitude"]

        )



    if "erro" in resultado:


        df.loc[i,"erro"] = (

            resultado["erro"]

        )



    time.sleep(1)



# ============================================================
# RESUMO
# ============================================================


print("\n")

print("="*60)

print("RESULTADO")

print("="*60)



print(

    df["status_geocode"]

    .value_counts()

)



print(

    "\nEncontrados:",

    (

        df["status_geocode"]

        =="encontrado"

    )

    .sum()

)



# ============================================================
# SALVAR
# ============================================================


df.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)



print("\nArquivo salvo:")

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