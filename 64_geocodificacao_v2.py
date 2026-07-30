# ============================================================
# 64_geocodificacao_v2.py
#
# Nova tentativa de geocodificação
#
# Estratégia:
# Endereco + Bairro + Joinville SC
#
# ============================================================

import pandas as pd
import numpy as np
import requests
import time
import os
import re


inicio = time.time()


print("="*70)
print("GEOCODIFICAÇÃO V2 - RECUPERAÇÃO DE ENDEREÇOS")
print("="*70)



ENTRADA = (
    "resultados/"
    "enderecos_geocodificados.csv"
)


SAIDA = (
    "resultados/"
    "geocodificacao_v2.csv"
)


RESUMO = (
    "resultados/"
    "resumo_geocodificacao_v2.csv"
)



# ------------------------------------------------------------
# leitura
# ------------------------------------------------------------

print("\nLendo arquivo...")


df = pd.read_csv(

    ENTRADA,

    low_memory=False

)



print(

    "Registros:",

    len(df)

)



# ------------------------------------------------------------
# função limpeza
# ------------------------------------------------------------

def limpar_endereco(x):

    if pd.isna(x):

        return ""

    x = str(x)


    x = re.sub(

        r"\bSN\b",

        "",

        x,

        flags=re.I

    )


    x = re.sub(

        r"\s+",

        " ",

        x

    )


    return x.strip()



# ------------------------------------------------------------
# somente sem coordenada
# ------------------------------------------------------------

df["latitude"] = pd.to_numeric(

    df["latitude"],

    errors="coerce"

)


df["longitude"] = pd.to_numeric(

    df["longitude"],

    errors="coerce"

)



pendentes = df[

    df["latitude"].isna()

].copy()



print(

    "Pendentes:",

    len(pendentes)

)



# ------------------------------------------------------------
# geocoder Nominatim
# ------------------------------------------------------------

session = requests.Session()

session.headers.update({

    "User-Agent":

    "pesquisa_censitario_joinville"

})



def geocodificar(endereco):

    try:

        r = session.get(

            "https://nominatim.openstreetmap.org/search",

            params={

                "q": endereco,

                "format": "json",

                "limit":1,

                "countrycodes":"br"

            },

            timeout=10

        )


        dados = r.json()


        if len(dados):

            return (

                float(dados[0]["lat"]),

                float(dados[0]["lon"])

            )


    except:

        pass


    return (

        np.nan,

        np.nan

    )



# ------------------------------------------------------------
# processamento
# ------------------------------------------------------------

novos = 0



print("\nIniciando...")


for i, idx in enumerate(pendentes.index):


    endereco = limpar_endereco(

        pendentes.loc[idx,"Endereco"]

    )


    bairro = str(

        pendentes.loc[idx,"Bairro"]

    )


    consulta = (

        endereco

        +

        ", "

        +

        bairro

        +

        ", Joinville SC"

    )



    lat, lon = geocodificar(

        consulta

    )



    if not np.isnan(lat):


        df.loc[idx,"latitude"] = lat

        df.loc[idx,"longitude"] = lon

        df.loc[idx,"status"] = "ENCONTRADO_V2"

        novos += 1



    if i % 100 == 0:

        print(

            i,

            "/",

            len(pendentes),

            "novos:",

            novos

        )


    time.sleep(1)



# ------------------------------------------------------------
# resumo
# ------------------------------------------------------------

total_coord = (

    df["latitude"]

    .notna()

    .sum()

)



resumo = pd.DataFrame({

    "indicador":[

        "total",

        "com_coordenada",

        "novas_v2",

        "sem_coordenada"

    ],

    "valor":[

        len(df),

        total_coord,

        novos,

        len(df)-total_coord

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