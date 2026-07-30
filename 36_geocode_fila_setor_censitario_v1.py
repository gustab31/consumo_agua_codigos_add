# ============================================================
# 36_geocode_fila_setor_censitario_v1.py
#
# GEOCODIFICAÇÃO DA FILA PRIORITÁRIA
#
# Objetivo:
# Endereço -> Coordenada -> Setor censitário IBGE
#
# ============================================================


import pandas as pd
import requests
import time
import os


inicio = time.time()


print("="*60)
print("GEOCODIFICACAO FILA SETOR CENSITARIO - V1")
print("="*60)



# ============================================================
# ARQUIVOS
# ============================================================


ENTRADA = (
    "resultados/"
    "fila_geocode_setor_prioridade_v1.csv"
)


SAIDA = (
    "resultados/"
    "geocode_fila_setor_censitario_v1.csv"
)



# ============================================================
# LER FILA
# ============================================================


print("\nLendo fila...")


df = pd.read_csv(

    ENTRADA,

    low_memory=False

)



print(

    "Registros:",

    len(df)

)



print(

    "Colunas:",

    df.columns.tolist()

)



# ============================================================
# PREPARAR CAMPOS
# ============================================================


def limpar_texto(x):

    if pd.isna(x):

        return ""

    return str(x).strip()



df["Endereco"] = df["Endereco"].apply(

    limpar_texto

)


df["Bairro"] = df["Bairro"].apply(

    limpar_texto

)



if "CEP" in df.columns:

    df["CEP"] = (

        df["CEP"]

        .astype(str)

        .str.replace(

            ".0",

            "",

            regex=False

        )

    )



# ============================================================
# CONSULTA
# ============================================================


def criar_consulta(row):


    partes = []


    partes.append(

        row["Endereco"]

    )


    partes.append(

        row["Bairro"]

    )


    partes.append(

        "Joinville SC Brasil"

    )


    return ", ".join(partes)



df["consulta"] = df.apply(

    criar_consulta,

    axis=1

)



# remover duplicados

antes = len(df)


df = df.drop_duplicates(

    "consulta"

)



print(

    "Duplicados removidos:",

    antes-len(df)

)



print(

    "Consultas:",

    len(df)

)

# ============================================================
# GEOCODIFICADOR
# ============================================================


def geocodificar(endereco):


    url = (

        "https://nominatim.openstreetmap.org/search"

    )


    parametros = {

        "q": endereco,

        "format": "json",

        "limit": 1,

        "countrycodes": "br"

    }



    try:


        resposta = requests.get(

            url,

            params=parametros,

            headers={

                "User-Agent":

                "pesquisa_setor_censitario"

            },

            timeout=15

        )



        dados = resposta.json()



        if len(dados) > 0:


            return (

                float(dados[0]["lat"]),

                float(dados[0]["lon"]),

                "encontrado",

                ""

            )



        else:


            return (

                None,

                None,

                "nao_encontrado",

                ""

            )



    except Exception as e:


        return (

            None,

            None,

            "erro",

            str(e)

        )



# ============================================================
# PROCESSAR FILA
# ============================================================


print("\nIniciando geocodificação...")


latitudes = []

longitudes = []

status = []

erros = []



total = len(df)



for i,row in df.iterrows():


    consulta = row["consulta"]



    lat,lon,stat,erro = geocodificar(

        consulta

    )


    latitudes.append(lat)

    longitudes.append(lon)

    status.append(stat)

    erros.append(erro)



    print(

        f"{i+1}/{total} - {consulta} - {stat}"

    )



    # respeitar limite do Nominatim

    time.sleep(1)



df["latitude"] = latitudes

df["longitude"] = longitudes

df["status_geocode"] = status

df["erro"] = erros



print("\nProcessamento concluído")



print(

    df["status_geocode"]

    .value_counts()

)

# ============================================================
# RESUMO
# ============================================================


resumo = pd.DataFrame({

    "indicador":[

        "total_enderecos",

        "encontrados",

        "nao_encontrados",

        "erros"

    ],

    "valor":[

        len(df),

        (

            df["status_geocode"]

            =="encontrado"

        ).sum(),


        (

            df["status_geocode"]

            =="nao_encontrado"

        ).sum(),


        (

            df["status_geocode"]

            =="erro"

        ).sum()

    ]

})



# ============================================================
# SALVAR
# ============================================================


print("\nSalvando arquivo...")


df.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)



ARQ_RESUMO = (

    "resultados/"

    "resumo_geocode_fila_setor_censitario_v1.csv"

)



resumo.to_csv(

    ARQ_RESUMO,

    index=False,

    encoding="utf-8-sig"

)



# ============================================================
# RESULTADO
# ============================================================


print("\n")

print("="*60)

print("RESULTADO FINAL")

print("="*60)


print(resumo)



print("\nArquivo:")

print(SAIDA)



print("\nResumo:")

print(ARQ_RESUMO)



print("\nTempo:")

print(

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim.")