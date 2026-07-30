# ============================================================
# 42_analise_similaridade_endereco_setor_v2.py
#
# SIMILARIDADE OTIMIZADA DE ENDERECOS COM CD_SETOR
#
# ============================================================


import pandas as pd
import numpy as np
import unicodedata
import time
import re
from difflib import SequenceMatcher


inicio = time.time()


print("="*60)
print("SIMILARIDADE ENDERECOS SETOR - V2 OTIMIZADA")
print("="*60)



ENTRADA = (
    "resultados/"
    "base_residencial_setor_geocode_fila_v1.csv"
)


SAIDA = (
    "resultados/"
    "analise_similaridade_setor_v2.csv"
)


RESUMO = (
    "resultados/"
    "resumo_similaridade_setor_v2.csv"
)



# ------------------------------------------------------------
# FUNÇÕES
# ------------------------------------------------------------


def normalizar(x):

    if pd.isna(x):
        return ""

    x = str(x).upper().strip()

    x = unicodedata.normalize(
        "NFKD",
        x
    ).encode(
        "ASCII",
        "ignore"
    ).decode(
        "ASCII"
    )

    return " ".join(x.split())



def tipo_via(x):

    x = normalizar(x)

    tipos = [

        "RUA",
        "ESTRADA",
        "RODOVIA",
        "SERVIDAO",
        "AVENIDA",
        "TRAVESSA",
        "ALAMEDA"

    ]

    for t in tipos:

        if x.startswith(t):

            return t

    return "OUTRO"



def primeira_palavra(x):

    x = normalizar(x)

    partes = x.split()

    if len(partes)>1:

        return partes[1]

    return ""



def score(a,b):

    return SequenceMatcher(

        None,

        a,

        b

    ).ratio()



# ------------------------------------------------------------
# LEITURA
# ------------------------------------------------------------


print("\nLendo base...")


df = pd.read_csv(

    ENTRADA,

    low_memory=False

)



print(

    "Shape:",

    df.shape

)



if "Endereco" in df.columns:

    col_end="Endereco"

else:

    col_end="endereco"



if "Bairro" in df.columns:

    col_bairro="Bairro"

else:

    col_bairro="bairro"



# ------------------------------------------------------------
# SEPARAÇÃO
# ------------------------------------------------------------


com = df[

    df["CD_SETOR"].notna()

].copy()



sem = df[

    df["CD_SETOR"].isna()

].copy()



print(

    "Com setor:",

    len(com)

)


print(

    "Sem setor:",

    len(sem)

)



# ------------------------------------------------------------
# NORMALIZAÇÃO
# ------------------------------------------------------------


print("\nPreparando chaves...")


for d in [com,sem]:

    d["end_norm"] = d[col_end].apply(normalizar)

    d["bairro_norm"] = d[col_bairro].apply(normalizar)

    d["tipo"] = d[col_end].apply(tipo_via)

    d["primeira"] = d[col_end].apply(primeira_palavra)



# somente endereços únicos

refs = (

    com[

        [

            "end_norm",

            "bairro_norm",

            "tipo",

            "primeira",

            "CD_SETOR"

        ]

    ]

    .drop_duplicates()

)



print(

    "Referências únicas:",

    len(refs)

)



# ------------------------------------------------------------
# INDEXAÇÃO
# ------------------------------------------------------------


print("\nCriando índice...")


indice = {}


for chave, grupo in refs.groupby(

    [

        "bairro_norm",

        "tipo",

        "primeira"

    ]

):

    indice[chave] = grupo



print(

    "Grupos índice:",

    len(indice)

)



# ------------------------------------------------------------
# PROCESSAMENTO
# ------------------------------------------------------------


print("\nComparando...")


resultado=[]


processados=0



for _,linha in sem.iterrows():


    chave=(

        linha["bairro_norm"],

        linha["tipo"],

        linha["primeira"]

    )


    candidatos = indice.get(

        chave

    )


    if candidatos is None:

        continue



    melhor=0

    setor=None



    for _,ref in candidatos.iterrows():


        s=score(

            linha["end_norm"],

            ref["end_norm"]

        )


        if s>melhor:

            melhor=s

            setor=ref["CD_SETOR"]



    if melhor>=0.90:


        resultado.append({

            "Endereco":

                linha[col_end],

            "Bairro":

                linha[col_bairro],

            "CD_SETOR_PROP":

                setor,

            "similaridade":

                round(melhor,3)

        })


    processados+=1


    if processados % 10000 == 0:

        print(

            "Processados:",

            processados

        )



# ------------------------------------------------------------
# RESULTADO
# ------------------------------------------------------------


out=pd.DataFrame(resultado)



resumo=pd.DataFrame({

    "indicador":[

        "sem_setor",

        "referencias",

        "candidatos"

    ],

    "valor":[

        len(sem),

        len(refs),

        len(out)

    ]

})



print("\n")

print("="*60)

print("RESULTADO")

print("="*60)

print(resumo)



print("\nAmostra:")

print(

    out.head(30)

)



out.to_csv(

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