# ============================================================
# 79_diagnostico_endereco.py
#
# DIAGNÓSTICO DO CAMPO ENDEREÇO
#
# Relatório 75
#
# ============================================================


import os
import re
import time
import warnings

import pandas as pd


warnings.filterwarnings("ignore")


inicio = time.time()



print("="*70)
print("DIAGNÓSTICO ENDEREÇOS RELATÓRIO 75")
print("="*70)



RESULTADOS = "resultados"



arquivo = os.path.join(

    RESULTADOS,

    "consumo_com_endereco.csv"

)



# ============================================================
# LER BASE
# ============================================================


print("\nLendo base...")


df = pd.read_csv(

    arquivo,

    encoding="utf-8-sig",

    low_memory=False

)



print(

    "Linhas:",

    len(df)

)



# ============================================================
# NORMALIZAÇÃO
# ============================================================


if "Endereco" not in df.columns:


    raise Exception(

        "Campo Endereco não encontrado."

    )



df["ENDERECO"] = (

    df["Endereco"]

    .astype(str)

    .str.upper()

    .str.strip()

)



df = df[

    df["ENDERECO"]

    != "NAN"

]



print(

    "Endereços únicos:",

    df["ENDERECO"]

    .nunique()

)



# ============================================================
# PADRÕES
# ============================================================



print("\nAnalisando padrões...")


diag = pd.DataFrame()


diag["ENDERECO"] = df["ENDERECO"]



diag["TAMANHO"] = (

    diag["ENDERECO"]

    .str.len()

)



diag["TEM_NUMERO"] = (

    diag["ENDERECO"]

    .str.contains(

        r"\d",

        regex=True

    )

)



diag["NUMEROS"] = (

    diag["ENDERECO"]

    .str.extract(

        r"(\d+)"

    )

)



diag["TEM_RUA"] = (

    diag["ENDERECO"]

    .str.contains(

        r"\b(RUA|R\.|AV|AVENIDA|ESTRADA|ROD|TRAVESSA|TRAV)\b",

        regex=True

    )

)



diag["TEM_CASA_APTO"] = (

    diag["ENDERECO"]

    .str.contains(

        r"CASA|APTO|APT|FUNDOS|SALA|BL",

        regex=True

    )

)



diag.to_excel(

    os.path.join(

        RESULTADOS,

        "diagnostico_enderecos.xlsx"

    ),

    index=False

)



# ============================================================
# ESTATÍSTICAS
# ============================================================



print("\nResumo:")


print(

    diag[

        [

            "TAMANHO",

            "TEM_NUMERO",

            "TEM_RUA",

            "TEM_CASA_APTO"

        ]

    ]

    .describe()

)



print("\nCom número:")

print(

    diag["TEM_NUMERO"]

    .value_counts()

)



print("\nCom padrão rua:")

print(

    diag["TEM_RUA"]

    .value_counts()

)



# ============================================================
# LOGRADOUROS FREQUENTES
# ============================================================


print("\nGerando logradouros...")


logradouro = (

    diag["ENDERECO"]

    .str.replace(

        r"\d+.*",

        "",

        regex=True

    )

    .str.strip()

)



freq = (

    logradouro

    .value_counts()

    .reset_index()

)



freq.columns = [

    "LOGRADOURO",

    "QUANTIDADE"

]



freq.head(500).to_excel(

    os.path.join(

        RESULTADOS,

        "logradouros_frequentes.xlsx"

    ),

    index=False

)



# ============================================================
# AMOSTRA
# ============================================================


diag.sample(

    min(5000,len(diag)),

    random_state=5

).to_excel(

    os.path.join(

        RESULTADOS,

        "amostra_endereco_detalhada.xlsx"

    ),

    index=False

)



print("\nArquivos gerados:")

print("- diagnostico_enderecos.xlsx")

print("- logradouros_frequentes.xlsx")

print("- amostra_endereco_detalhada.xlsx")



print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim Código 79.")