# ============================================================
# 52_inferencia_setor_cadastral_v2.py
#
# Inferência de setor censitário por padrões cadastrais
#
# ============================================================

import os
import time
import pandas as pd


inicio = time.time()


print("="*70)
print("INFERÊNCIA DE SETOR CENSITÁRIO")
print("="*70)


# ------------------------------------------------------------
# arquivos
# ------------------------------------------------------------

ENTRADA = (
    "resultados/"
    "base_residencial_setor_logradouro_normalizado_v3.csv"
)

SAIDA = (
    "resultados/"
    "base_inferencia_setor_v2.csv"
)

RESUMO = (
    "resultados/"
    "resumo_inferencia_setor_v2.csv"
)


# ------------------------------------------------------------
# leitura
# ------------------------------------------------------------

print("\nLendo base...")


df = pd.read_csv(
    ENTRADA,
    low_memory=False
)


print("Shape:", df.shape)


# ------------------------------------------------------------
# garantir CD_SETOR como texto
# ------------------------------------------------------------

if "CD_SETOR" not in df.columns:

    raise Exception(
        "Coluna CD_SETOR não encontrada"
    )


df["CD_SETOR"] = (
    df["CD_SETOR"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ------------------------------------------------------------
# criar colunas novas como texto
# ------------------------------------------------------------

for col in [
    "CD_SETOR_PROVAVEL",
    "metodo_atribuicao",
    "confianca"
]:

    df[col] = ""


# ------------------------------------------------------------
# separar bases
# ------------------------------------------------------------

com = df[
    df["CD_SETOR"] != ""
].copy()


sem = df[
    df["CD_SETOR"] == ""
].copy()


print("\nCom setor:", len(com))
print("Sem setor:", len(sem))


# ------------------------------------------------------------
# padronização texto
# ------------------------------------------------------------

campos = [
    "Endereco",
    "Bairro",
    "CEP"
]


for base in [com, sem]:

    for c in campos:

        if c not in base.columns:

            base[c] = ""

        base[c] = (

            base[c]
            .fillna("")
            .astype(str)
            .str.upper()
            .str.strip()

        )


# ------------------------------------------------------------
# REGRA 1
# mesmo endereço + bairro
# ------------------------------------------------------------

print("\nAplicando regra endereço + bairro...")


ref = (

    com

    .groupby(
        [
            "Endereco",
            "Bairro"
        ]
    )["CD_SETOR"]

    .agg(
        lambda x:
        x.value_counts().index[0]
    )

)


novos1 = 0


for idx,row in sem.iterrows():


    chave = (
        row["Endereco"],
        row["Bairro"]
    )


    if chave in ref.index:


        sem.at[
            idx,
            "CD_SETOR_PROVAVEL"
        ] = str(
            ref.loc[chave]
        )


        sem.at[
            idx,
            "metodo_atribuicao"
        ] = (
            "mesmo_endereco_bairro"
        )


        sem.at[
            idx,
            "confianca"
        ] = "ALTA"


        novos1 += 1



print(
    "Novos por endereço:",
    novos1
)


# ------------------------------------------------------------
# REGRA 2
# logradouro + bairro dominante
# ------------------------------------------------------------

print("\nAplicando regra dominante...")


contagem = (

    com

    .groupby(
        [
            "Endereco",
            "Bairro",
            "CD_SETOR"
        ]
    )

    .size()

    .reset_index(
        name="n"
    )

)


totais = (

    contagem

    .groupby(
        [
            "Endereco",
            "Bairro"
        ]
    )["n"]

    .sum()

)


contagem["total"] = (

    contagem.apply(

        lambda x:

        totais[
            (
                x["Endereco"],
                x["Bairro"]
            )
        ],

        axis=1

    )

)


contagem["perc"] = (

    contagem["n"]

    /

    contagem["total"]

)


dominante = contagem[

    contagem["perc"] >= 0.95

]


mapa = (

    dominante

    .drop_duplicates(
        [
            "Endereco",
            "Bairro"
        ]
    )

    .set_index(
        [
            "Endereco",
            "Bairro"
        ]
    )["CD_SETOR"]

)


novos2 = 0


for idx,row in sem.iterrows():


    if sem.at[
        idx,
        "CD_SETOR_PROVAVEL"
    ] != "":

        continue


    chave = (
        row["Endereco"],
        row["Bairro"]
    )


    if chave in mapa.index:


        sem.at[
            idx,
            "CD_SETOR_PROVAVEL"
        ] = str(
            mapa.loc[chave]
        )


        sem.at[
            idx,
            "metodo_atribuicao"
        ] = (
            "logradouro_dominante"
        )


        sem.at[
            idx,
            "confianca"
        ] = "MEDIA"


        novos2 += 1



print(
    "Novos por dominante:",
    novos2
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


# ------------------------------------------------------------
# resumo
# ------------------------------------------------------------

total_inferidos = (

    resultado[
        "CD_SETOR_PROVAVEL"
    ]
    != ""
).sum()



resumo = pd.DataFrame(

    {

        "indicador":[

            "total_registros",

            "com_setor_original",

            "sem_setor_original",

            "novas_inferencias"

        ],


        "valor":[

            len(resultado),

            len(com),

            len(sem),

            total_inferidos

        ]

    }

)



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


resultado.to_csv(
    SAIDA,
    index=False,
    encoding="utf-8-sig"
)


resumo.to_csv(
    RESUMO,
    index=False,
    encoding="utf-8-sig"
)


print("\nArquivos gerados:")
print(SAIDA)
print(RESUMO)


print(
    "\nTempo:",
    round(
        time.time()-inicio,
        2
    ),
    "segundos"
)


print("\nFim.")