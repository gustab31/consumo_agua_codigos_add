import os
import time
import pandas as pd
import requests


print("="*70)
print("GEOCODIFICAÇÃO PRIORITÁRIA")
print("="*70)


ENTRADA = "resultados/enderecos_unicos_padronizados.csv"

SAIDA = "resultados/enderecos_geocodificados_prioritarios.csv"


# ============================================================
# LEITURA
# ============================================================


df = pd.read_csv(

    ENTRADA,

    low_memory=False

)


print("\nTotal endereços:")

print(len(df))



# ============================================================
# CORREÇÃO DOS TIPOS
# ============================================================


# numéricas

for c in [

    "latitude",

    "longitude",

    "importance"

]:


    if c not in df.columns:

        df[c] = pd.Series(

            dtype="float64"

        )

    else:

        df[c] = pd.to_numeric(

            df[c],

            errors="coerce"

        )



# texto

for c in [

    "display_name",

    "osm_type",

    "status",

    "fonte"

]:


    if c not in df.columns:

        df[c] = ""


    df[c] = df[c].astype(

        "object"

    )



print("\nTipos corrigidos")

print(df[[

    "latitude",

    "longitude",

    "status"

]].dtypes)