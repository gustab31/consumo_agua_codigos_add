# ============================================================
# 25_gerar_fila_geocodificacao_prioridade_v2.py
#
# Cria fila inteligente de geocodificacao
# após propagacao de CD_SETOR
#
# ============================================================


import pandas as pd
import os
import time


inicio = time.time()


print("="*60)
print("GERANDO FILA DE GEOCODIFICACAO PRIORIDADE V2")
print("="*60)



ARQ_BASE = (
    "resultados/"
    "base_residencial_setor_propagado_v2.csv"
)


SAIDA_FILA = (
    "resultados/"
    "fila_geocodificacao_prioridade_alta_v2.csv"
)


SAIDA_RESUMO = (
    "resultados/"
    "resumo_fila_geocodificacao_v2.csv"
)



# ============================================================
# LEITURA
# ============================================================


print("\nLendo base...")


if not os.path.exists(ARQ_BASE):

    raise FileNotFoundError(ARQ_BASE)



df = pd.read_csv(

    ARQ_BASE,

    low_memory=False

)



print(

    "Shape:",

    df.shape

)



# ============================================================
# LOCALIZAR COLUNAS
# ============================================================


def achar(df, nomes):

    for n in nomes:

        if n in df.columns:

            return n

    return None



endereco = achar(

    df,

    [
        "Endereco",
        "endereco"
    ]

)


bairro = achar(

    df,

    [
        "Bairro",
        "bairro"
    ]

)


cep = achar(

    df,

    [
        "CEP",
        "cep"
    ]

)



if endereco is None or bairro is None:

    raise Exception(
        "Endereco ou bairro não encontrados"
    )



print(

    "Colunas:",

    endereco,

    bairro,

    cep

)



# ============================================================
# FILTRAR SEM SETOR
# ============================================================


print("\nSelecionando matrículas sem setor...")


sem = df[

    df["CD_SETOR"].isna()

].copy()



print(

    "Sem setor:",

    len(sem)

)



# ============================================================
# CHAVES
# ============================================================


sem["_END"] = (

    sem[endereco]

    .astype(str)

    .str.upper()

    .str.strip()

)



sem["_BAIRRO"] = (

    sem[bairro]

    .astype(str)

    .str.upper()

    .str.strip()

)



# ============================================================
# AGRUPAR
# ============================================================


print("\nAgrupando endereços...")


fila = (

    sem

    .groupby(

        [

            "_END",

            "_BAIRRO"

        ]

    )

    .agg(

        total_matriculas=(

            "MATRICULA",

            "count"

        ),

        matriculas=(

            "MATRICULA",

            lambda x:

            ";".join(

                x.astype(str)

            )

        )

    )

    .reset_index()

)



fila.rename(

    columns={

        "_END":"endereco",

        "_BAIRRO":"bairro"

    },

    inplace=True

)



# ============================================================
# CEP POR ENDEREÇO
# ============================================================


if cep:


    mapa_cep = (

        sem

        .groupby(

            [

                "_END",

                "_BAIRRO"

            ]

        )[cep]

        .first()

        .reset_index()

    )


    mapa_cep.rename(

        columns={

            "_END":"endereco",

            "_BAIRRO":"bairro",

            cep:"CEP"

        },

        inplace=True

    )


    fila = fila.merge(

        mapa_cep,

        on=[

            "endereco",

            "bairro"

        ],

        how="left"

    )



# ============================================================
# PRIORIDADE
# ============================================================


def classificar(n):

    if n >= 100:

        return "MUITO_ALTA"

    elif n >= 30:

        return "ALTA"

    elif n >= 10:

        return "MEDIA"

    else:

        return "BAIXA"



fila["prioridade"] = (

    fila["total_matriculas"]

    .apply(classificar)

)



# manter somente interessante


fila = fila[

    fila["prioridade"]

    .isin(

        [

            "MUITO_ALTA",

            "ALTA",

            "MEDIA"

        ]

    )

]



fila.sort_values(

    "total_matriculas",

    ascending=False,

    inplace=True

)



# ============================================================
# RESUMO
# ============================================================


resumo = (

    fila

    .groupby(

        "prioridade"

    )

    [

        "total_matriculas"

    ]

    .agg(

        [

            "count",

            "sum"

        ]

    )

    .reset_index()

)



resumo.columns = [

    "prioridade",

    "enderecos",

    "matriculas"

]



# ============================================================
# SALVAR
# ============================================================


fila.to_csv(

    SAIDA_FILA,

    index=False,

    encoding="utf-8-sig"

)



resumo.to_csv(

    SAIDA_RESUMO,

    index=False,

    encoding="utf-8-sig"

)



# ============================================================
# FINAL
# ============================================================


print("\n")

print("="*60)

print("RESULTADO")

print("="*60)


print(resumo)



print("\nTotal endereços fila:")

print(len(fila))


print("\nTop 20:")

print(

    fila.head(20)

)



print("\nArquivos:")

print(SAIDA_FILA)

print(SAIDA_RESUMO)



print("\nTempo:")

print(

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)


print("\nFim.")