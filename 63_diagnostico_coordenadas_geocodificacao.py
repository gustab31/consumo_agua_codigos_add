# ============================================================
# 63_diagnostico_coordenadas_geocodificacao.py
#
# Verifica qualidade do arquivo:
# enderecos_geocodificados.csv
#
# ============================================================

import pandas as pd
import os
import time


inicio = time.time()


print("="*70)
print("DIAGNÓSTICO DE COORDENADAS DA GEOCODIFICAÇÃO")
print("="*70)



ARQUIVO = (
    "resultados/"
    "enderecos_geocodificados.csv"
)


SAIDA = (
    "resultados/"
    "diagnostico_coordenadas_geo.csv"
)



# ------------------------------------------------------------
# leitura
# ------------------------------------------------------------

print("\nLendo arquivo...")


geo = pd.read_csv(

    ARQUIVO,

    low_memory=False

)



print(
    "Registros:",
    len(geo)
)



print("\nColunas:")

print(
    list(geo.columns)
)



# ------------------------------------------------------------
# verificar latitude longitude
# ------------------------------------------------------------

resultado = []



for campo in [

    "latitude",

    "longitude"

]:

    if campo in geo.columns:


        geo[campo+"_num"] = pd.to_numeric(

            geo[campo],

            errors="coerce"

        )


        validos = (

            geo[campo+"_num"]

            .notna()

            .sum()

        )


        resultado.append({

            "campo": campo,

            "tipo_original":

                str(geo[campo].dtype),

            "validos":

                validos,

            "percentual":

                round(

                    validos /
                    len(geo)
                    *
                    100,

                    2

                ),

            "min":

                geo[campo+"_num"].min(),

            "max":

                geo[campo+"_num"].max()

        })



# ------------------------------------------------------------
# procurar campos candidatos
# ------------------------------------------------------------

print("\nCampos possíveis de coordenada:")


for c in geo.columns:

    if any(

        x in c.lower()

        for x in [

            "lat",

            "lon",

            "coord",

            "x",

            "y"

        ]

    ):

        print(c)



# ------------------------------------------------------------
# exemplos
# ------------------------------------------------------------

print("\nPrimeiros registros:")


cols = [

    c for c in [

        "Endereco",

        "Bairro",

        "latitude",

        "longitude",

        "status"

    ]

    if c in geo.columns

]


print(

    geo[cols]

    .head(10)

)



# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

resumo = pd.DataFrame(resultado)



os.makedirs(

    "resultados",

    exist_ok=True

)



resumo.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)



print("\n")
print("="*70)
print("RESUMO")
print("="*70)


print(resumo)



print("\nArquivo:")

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