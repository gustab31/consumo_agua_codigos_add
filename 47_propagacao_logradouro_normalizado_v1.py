# ============================================================
# 47_propagacao_logradouro_normalizado_v3.py
#
# PROPAGACAO CD_SETOR POR LOGRADOURO NORMALIZADO
#
# VERSAO ROBUSTA
#
# Corrige:
# - KeyError CD_SETOR_PROP
# - erro replace([]) pandas
# - conflito dtype float/string
# - merges sem coluna
#
# ============================================================


import pandas as pd
import numpy as np
import os
import re
import unicodedata
import time


inicio = time.time()


print("=" * 70)
print("PROPAGACAO LOGRADOURO NORMALIZADO - V3")
print("=" * 70)


# ------------------------------------------------------------
# arquivos
# ------------------------------------------------------------

entrada = (
    "resultados/"
    "base_residencial_setor_propagacao_controlada_v1.csv"
)


saida = (
    "resultados/"
    "base_residencial_setor_logradouro_normalizado_v3.csv"
)


arquivo_resumo = (
    "resultados/"
    "resumo_logradouro_normalizado_v3.csv"
)



# ------------------------------------------------------------
# leitura
# ------------------------------------------------------------

print("\nLendo base...")


if not os.path.exists(entrada):

    raise FileNotFoundError(
        f"Arquivo não encontrado: {entrada}"
    )


df = pd.read_csv(
    entrada,
    low_memory=False
)


print(
    "Shape:",
    df.shape
)



# ------------------------------------------------------------
# validação
# ------------------------------------------------------------

necessarias = [

    "Endereco",
    "Bairro",
    "CD_SETOR"

]


faltando = [

    c for c in necessarias
    if c not in df.columns

]


if faltando:

    raise Exception(
        f"Colunas ausentes: {faltando}"
    )



# ------------------------------------------------------------
# limpeza segura CD_SETOR
# ------------------------------------------------------------

print("\nLimpando CD_SETOR...")


def limpar_setor(x):

    if pd.isna(x):

        return pd.NA


    x = str(x).strip()


    if x in [

        "",
        "nan",
        "None",
        "[]"

    ]:

        return pd.NA


    return x



df["CD_SETOR"] = (

    df["CD_SETOR"]

    .apply(limpar_setor)

    .astype("string")

)



print(
    "Com setor antes:",
    df["CD_SETOR"].notna().sum()
)



# ------------------------------------------------------------
# normalização endereço
# ------------------------------------------------------------

def normalizar(valor):

    if pd.isna(valor):

        return ""


    valor = str(valor).upper()


    valor = unicodedata.normalize(
        "NFKD",
        valor
    )


    valor = (
        valor
        .encode(
            "ASCII",
            "ignore"
        )
        .decode()
    )


    valor = re.sub(
        r"\d+",
        " ",
        valor
    )


    valor = re.sub(
        r"[^A-Z ]",
        " ",
        valor
    )


    valor = re.sub(
        r"\s+",
        " ",
        valor
    )


    return valor.strip()



print("\nCriando chaves...")


df["logradouro_norm"] = (

    df["Endereco"]

    .apply(normalizar)

)


df["bairro_norm"] = (

    df["Bairro"]

    .apply(normalizar)

)



df["chave_logradouro"] = (

    df["logradouro_norm"]

    + "|"

    + df["bairro_norm"]

)



print("Chaves criadas")

# ------------------------------------------------------------
# criação da referência de setores
# ------------------------------------------------------------

print("\nCriando referência...")


referencia = df[

    df["CD_SETOR"].notna()

].copy()



print(

    "Registros referência:",

    len(referencia)

)



if len(referencia) == 0:

    raise Exception(
        "Não existem registros com CD_SETOR para criar referência"
    )



# ------------------------------------------------------------
# setores dominantes por logradouro
# ------------------------------------------------------------


print("\nCalculando setores dominantes...")


contagem = (

    referencia

    .groupby(

        [

            "chave_logradouro",

            "CD_SETOR"

        ]

    )

    .size()

    .reset_index(

        name="qtd"

    )

)



totais = (

    referencia

    .groupby(

        "chave_logradouro"

    )

    .size()

    .reset_index(

        name="total"

    )

)



dominante = (

    contagem

    .sort_values(

        [

            "chave_logradouro",

            "qtd"

        ],

        ascending=[

            True,

            False

        ]

    )

    .drop_duplicates(

        "chave_logradouro"

    )

)



dominante = dominante.merge(

    totais,

    on="chave_logradouro",

    how="left"

)



dominante["percentual"] = (

    dominante["qtd"]

    /

    dominante["total"]

)



dominante = dominante.rename(

    columns={

        "CD_SETOR":

        "CD_SETOR_PROP"

    }

)



# regra conservadora

dominante = dominante[

    (dominante["total"] >= 5)

    &

    (dominante["percentual"] >= 0.85)

].copy()



print(

    "Logradouros dominantes:",

    len(dominante)

)



# ------------------------------------------------------------
# separação registros sem setor
# ------------------------------------------------------------


print("\nAplicando propagação...")


sem = df[

    df["CD_SETOR"].isna()

].copy()



com = df[

    df["CD_SETOR"].notna()

].copy()



print(

    "Sem setor:",

    len(sem)

)



# ------------------------------------------------------------
# merge seguro
# ------------------------------------------------------------


if len(dominante) > 0:


    sem = sem.merge(

        dominante[

            [

                "chave_logradouro",

                "CD_SETOR_PROP",

                "percentual"

            ]

        ],

        on="chave_logradouro",

        how="left"

    )


else:


    sem["CD_SETOR_PROP"] = pd.NA

    sem["percentual"] = pd.NA



# garante coluna

if "CD_SETOR_PROP" not in sem.columns:

    sem["CD_SETOR_PROP"] = pd.NA



print(

    "Candidatos encontrados:",

    sem["CD_SETOR_PROP"].notna().sum()

)

# ------------------------------------------------------------
# aplicar setores encontrados
# ------------------------------------------------------------

print("\nTransferindo setores...")


novos = sem[

    "CD_SETOR_PROP"

].notna().sum()



# recebe setor propagado

sem.loc[

    sem["CD_SETOR_PROP"].notna(),

    "CD_SETOR"

] = sem.loc[

    sem["CD_SETOR_PROP"].notna(),

    "CD_SETOR_PROP"

]



# garante string

sem["CD_SETOR"] = (

    sem["CD_SETOR"]

    .astype("string")

)



# ------------------------------------------------------------
# juntar novamente
# ------------------------------------------------------------

resultado = pd.concat(

    [

        com,

        sem

    ],

    ignore_index=True

)



# remove colunas auxiliares se existirem

resultado = resultado.drop(

    columns=[

        "CD_SETOR_PROP",

        "percentual"

    ],

    errors="ignore"

)



# ------------------------------------------------------------
# estatísticas finais
# ------------------------------------------------------------


total = len(resultado)


com_setor = (

    resultado["CD_SETOR"]

    .notna()

    .sum()

)


sem_setor = (

    resultado["CD_SETOR"]

    .isna()

    .sum()

)



percentual = (

    com_setor

    /

    total

    *

    100

)



print("\n")
print("=" * 60)
print("RESULTADO FINAL")
print("=" * 60)


resumo = pd.DataFrame(

    {

        "indicador":[

            "total_registros",

            "com_setor_final",

            "novos_setores_propagados",

            "sem_setor_final",

            "percentual_cobertura"

        ],

        "valor":[

            total,

            com_setor,

            novos,

            sem_setor,

            round(percentual,2)

        ]

    }

)



print(resumo)



# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------


print("\nSalvando arquivos...")


os.makedirs(

    "resultados",

    exist_ok=True

)



resultado.to_csv(

    saida,

    index=False,

    encoding="utf-8-sig"

)



resumo.to_csv(

    arquivo_resumo,

    index=False,

    encoding="utf-8-sig"

)



print("\nArquivos:")

print(saida)

print(arquivo_resumo)



tempo = round(

    time.time()

    -

    inicio,

    2

)


print("\nTempo:")

print(

    tempo,

    "segundos"

)


print("\nFim.")