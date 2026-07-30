# ============================================================
# 28_propagacao_similaridade_endereco_v1.py
#
# Propagação CD_SETOR por similaridade de endereço
#
# ============================================================


import pandas as pd
import re
import unicodedata
import time
import os


inicio = time.time()


print("="*60)
print("PROPAGANDO CD_SETOR POR SIMILARIDADE DE ENDEREÇO")
print("="*60)



# ============================================================
# ARQUIVOS
# ============================================================


ENTRADA = (
    "resultados/"
    "base_residencial_setor_propagado_v2.csv"
)


SAIDA = (
    "resultados/"
    "base_residencial_setor_similaridade_v1.csv"
)


RESUMO = (
    "resultados/"
    "resumo_similaridade_setor_v1.csv"
)



# ============================================================
# LEITURA
# ============================================================


if not os.path.exists(ENTRADA):

    raise FileNotFoundError(
        ENTRADA
    )


print("\nLendo base...")


df = pd.read_csv(

    ENTRADA,

    low_memory=False

)


print(

    "Shape:",

    df.shape

)



# ============================================================
# GARANTIR CD_SETOR
# ============================================================


if "CD_SETOR" not in df.columns:

    df["CD_SETOR"] = None



df["CD_SETOR"] = (

    df["CD_SETOR"]

    .replace(

        "",

        pd.NA

    )

)



# ============================================================
# FUNÇÃO NORMALIZAÇÃO
# ============================================================


def normalizar(texto):

    if pd.isna(texto):

        return ""


    texto = str(texto).upper()


    texto = (

        unicodedata

        .normalize(

            "NFKD",

            texto

        )

        .encode(

            "ASCII",

            "ignore"

        )

        .decode()

    )


    # remove números

    texto = re.sub(

        r"\d+",

        "",

        texto

    )


    # remove caracteres

    texto = re.sub(

        r"[^A-Z]",

        "",

        texto

    )


    return texto



# ============================================================
# CRIAR CHAVES
# ============================================================


print("\nCriando chaves...")


df["END_SIMILAR"] = (

    df["Endereco"]

    .apply(normalizar)

)


df["BAIRRO_SIMILAR"] = (

    df["Bairro"]

    .apply(normalizar)

)



# ============================================================
# BASE DE REFERÊNCIA
# ============================================================


referencia = df[

    df["CD_SETOR"]

    .notna()

].copy()



print(

    "Registros com setor:",

    len(referencia)

)



# mapa endereço/bairro -> setores


mapa = (

    referencia

    .groupby(

        [

            "END_SIMILAR",

            "BAIRRO_SIMILAR"

        ]

    )["CD_SETOR"]

    .unique()

)



# ============================================================
# TRANSFERÊNCIA
# ============================================================


print("\nTransferindo setores...")


novos = 0

conflitos = 0


lista_setor = []

lista_metodo = []



for _, linha in df.iterrows():


    # já possui setor

    if pd.notna(

        linha["CD_SETOR"]

    ):


        lista_setor.append(

            linha["CD_SETOR"]

        )


        lista_metodo.append(

            "existente"

        )


        continue



    chave = (

        linha["END_SIMILAR"],

        linha["BAIRRO_SIMILAR"]

    )



    if chave in mapa.index:


        setores = mapa[chave]



        if len(setores) == 1:


            lista_setor.append(

                setores[0]

            )


            lista_metodo.append(

                "similaridade_endereco"

            )


            novos += 1



        else:


            lista_setor.append(

                pd.NA

            )


            lista_metodo.append(

                "conflito"

            )


            conflitos += 1



    else:


        lista_setor.append(

            pd.NA

        )


        lista_metodo.append(

            None

        )



df["CD_SETOR"] = lista_setor


df["metodo_setor"] = lista_metodo



# ============================================================
# RESUMO
# ============================================================


total = len(df)


com_setor = (

    df["CD_SETOR"]

    .notna()

    .sum()

)



resumo = pd.DataFrame(

    {

        "indicador":[

            "total_registros",

            "com_CD_SETOR",

            "sem_CD_SETOR",

            "novos_por_similaridade",

            "conflitos",

            "percentual"

        ],


        "valor":[

            total,

            com_setor,

            total-com_setor,

            novos,

            conflitos,

            round(

                com_setor /

                total *

                100,

                2

            )

        ]

    }

)



# ============================================================
# SALVAR
# ============================================================


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



# ============================================================
# RESULTADO
# ============================================================


print("\n")

print("="*60)

print("RESULTADO")

print("="*60)


print(resumo)



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