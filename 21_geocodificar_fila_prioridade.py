# ============================================================
# 21_geocodificar_fila_prioridade_v4.py
# ============================================================

import pandas as pd
import time
import requests
from urllib.parse import quote


inicio = time.time()


print("="*60)
print("GEOCODIFICANDO FILA PRIORIDADE ALTA - V4")
print("="*60)



# ============================================================
# ARQUIVOS
# ============================================================

ENTRADA = (
    "resultados/"
    "geocode_prioridade_alta_resultado.csv"
)

SAIDA = (
    "resultados/"
    "geocode_prioridade_alta_resultado.csv"
)



# ============================================================
# LEITURA
# ============================================================

print("\nLendo fila...")


df = pd.read_csv(
    ENTRADA,
    low_memory=False,
    dtype=str
)


print(
    "Registros:",
    len(df)
)



# ============================================================
# GARANTIR COLUNAS COMO TEXTO
# ============================================================

controle = [

    "latitude",
    "longitude",
    "status_geocode",
    "consulta",
    "erro"

]


for col in controle:


    if col not in df.columns:

        df[col] = ""


    else:

        df[col] = df[col].fillna("").astype(str)



# ============================================================
# FUNÇÃO GEOCODIFICAÇÃO
# ============================================================


def geocodificar(endereco, bairro):


    consulta = (

        f"{endereco}, "
        f"{bairro}, "
        "Joinville SC Brasil"

    )


    url = (

        "https://nominatim.openstreetmap.org/search?"

        f"q={quote(consulta)}"

        "&format=json"

        "&limit=1"

    )


    headers = {

        "User-Agent":
        "pesquisa_censitario_agua"

    }


    try:


        r = requests.get(

            url,

            headers=headers,

            timeout=20

        )


        dados = r.json()



        if len(dados) > 0:


            return {

                "latitude":
                dados[0]["lat"],

                "longitude":
                dados[0]["lon"],

                "status":
                "encontrado",

                "consulta":
                consulta,

                "erro":
                ""

            }



        return {

            "latitude":
            "",

            "longitude":
            "",

            "status":
            "nao_encontrado",

            "consulta":
            consulta,

            "erro":
            ""

        }



    except Exception as e:


        return {

            "latitude":
            "",

            "longitude":
            "",

            "status":
            "erro",

            "consulta":
            consulta,

            "erro":
            str(e)

        }



# ============================================================
# PROCESSAMENTO
# ============================================================


print("\nIniciando...")


contador = 0


for i,row in df.iterrows():


    status = row["status_geocode"]



    # pula apenas finalizados

    if status in [

        "encontrado",

        "nao_encontrado",

        "erro"

    ]:

        continue



    contador += 1



    print(

        f"{contador}/{len(df)} - "

        f"{row['endereco']}"

    )



    resultado = geocodificar(

        row["endereco"],

        row["bairro"]

    )



    df.at[i,"latitude"] = resultado["latitude"]

    df.at[i,"longitude"] = resultado["longitude"]

    df.at[i,"status_geocode"] = resultado["status"]

    df.at[i,"consulta"] = resultado["consulta"]

    df.at[i,"erro"] = resultado["erro"]



    if contador % 10 == 0:


        df.to_csv(

            SAIDA,

            index=False,

            encoding="utf-8-sig"

        )


        print(

            "Salvo parcial:",

            contador

        )



    time.sleep(1)



# ============================================================
# SALVAR
# ============================================================


df.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)



print("\n")
print("="*60)
print("RESULTADO FINAL")
print("="*60)



print(

    df["status_geocode"]

    .value_counts()

)



print("\nEncontrados:")


print(

    (df["status_geocode"]=="encontrado")

    .sum()

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