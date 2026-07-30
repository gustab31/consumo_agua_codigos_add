# ============================================================
# TRANSFERIR CD_SETOR POR ENDEREÇO COMPARTILHADO
# ============================================================

import pandas as pd
import os
import re
import unicodedata
import time

inicio = time.time()

print("="*60)
print("TRANSFERINDO CD_SETOR POR ENDEREÇO")
print("="*60)


# ------------------------------------------------------------
# Caminhos
# ------------------------------------------------------------

ARQ_RESIDENCIAL = "resultados/base_residencial_p99.csv"

ARQ_ESPACIAL_1 = "resultados/base_geocodificada.csv"
ARQ_ESPACIAL_2 = "resultados/base_final_espacial.csv"

SAIDA = "resultados/base_residencial_setor_endereco.csv"


# ------------------------------------------------------------
# Função normalização
# ------------------------------------------------------------

def normalizar(texto):

    if pd.isna(texto):
        return ""

    texto = str(texto).upper()

    texto = unicodedata.normalize(
        "NFKD",
        texto
    ).encode(
        "ASCII",
        "ignore"
    ).decode(
        "ASCII"
    )

    texto = re.sub(
        r'[^A-Z0-9]',
        '',
        texto
    )

    return texto


# ------------------------------------------------------------
# Ler residencial
# ------------------------------------------------------------

print("\nLendo residencial...")

df = pd.read_csv(
    ARQ_RESIDENCIAL,
    low_memory=False
)

print(df.shape)


# ------------------------------------------------------------
# Ler bases com setor
# ------------------------------------------------------------

bases = []


for arq in [ARQ_ESPACIAL_1, ARQ_ESPACIAL_2]:

    if os.path.exists(arq):

        print("\nEncontrado:")
        print(arq)

        temp = pd.read_csv(
            arq,
            low_memory=False
        )

        if (
            "matricula" in temp.columns
            and "CD_SETOR" in temp.columns
        ):

            temp = temp[
                [
                    "matricula",
                    "CD_SETOR"
                ]
            ]

            temp.columns = [
                "MATRICULA",
                "CD_SETOR"
            ]

            bases.append(temp)



# ------------------------------------------------------------
# Criar tabela conhecida
# ------------------------------------------------------------

if len(bases) > 0:

    setor = pd.concat(
        bases,
        ignore_index=True
    )

    setor = setor.dropna(
        subset=["CD_SETOR"]
    )

    setor["MATRICULA"] = (
        setor["MATRICULA"]
        .astype(str)
        .str.replace(
            ".0",
            "",
            regex=False
        )
    )

    setor = setor.drop_duplicates()

else:

    setor = pd.DataFrame(
        columns=[
            "MATRICULA",
            "CD_SETOR"
        ]
    )


print("\nSetores conhecidos:")
print(setor.shape)


# ------------------------------------------------------------
# Merge por matrícula
# ------------------------------------------------------------

print("\nTransferência por matrícula...")


df["MATRICULA"] = (
    df["MATRICULA"]
    .astype(str)
)


df = df.merge(
    setor,
    on="MATRICULA",
    how="left"
)


df["metodo_setor"] = ""
df["confianca"] = ""


mask = df["CD_SETOR"].notna()

df.loc[
    mask,
    "metodo_setor"
] = "matricula"

df.loc[
    mask,
    "confianca"
] = "alta"


print(
    "Encontrados por matrícula:",
    mask.sum()
)


# ------------------------------------------------------------
# Criar chave endereço
# ------------------------------------------------------------

print("\nCriando chave endereço...")


df["ENDERECO_CHAVE"] = (
    df["Endereco"].fillna("")
    + "_"
    + df["Bairro"].fillna("")
)


df["ENDERECO_CHAVE"] = (
    df["ENDERECO_CHAVE"]
    .apply(normalizar)
)



# ------------------------------------------------------------
# Criar tabela endereço -> setor
# ------------------------------------------------------------

print("\nCriando tabela endereço/setor...")


conhecidos = df[
    df["CD_SETOR"].notna()
]


mapa_endereco = (
    conhecidos
    .groupby("ENDERECO_CHAVE")
    ["CD_SETOR"]
    .nunique()
)


enderecos_validos = mapa_endereco[
    mapa_endereco == 1
].index


print(
    "Endereços com setor único:",
    len(enderecos_validos)
)


tabela_endereco = (
    conhecidos[
        conhecidos["ENDERECO_CHAVE"]
        .isin(enderecos_validos)
    ]
    [
        [
            "ENDERECO_CHAVE",
            "CD_SETOR"
        ]
    ]
    .drop_duplicates()
)


# ------------------------------------------------------------
# Transferir por endereço
# ------------------------------------------------------------

print("\nTransferindo por endereço...")


faltantes = df[
    df["CD_SETOR"].isna()
].copy()


faltantes = faltantes.merge(
    tabela_endereco,
    on="ENDERECO_CHAVE",
    how="left",
    suffixes=(
        "",
        "_NOVO"
    )
)


mask = faltantes["CD_SETOR_NOVO"].notna()


faltantes.loc[
    mask,
    "CD_SETOR"
] = faltantes.loc[
    mask,
    "CD_SETOR_NOVO"
]


faltantes.loc[
    mask,
    "metodo_setor"
] = "endereco_compartilhado"


faltantes.loc[
    mask,
    "confianca"
] = "alta"



# ------------------------------------------------------------
# Atualizar base
# ------------------------------------------------------------

df_final = pd.concat(
    [
        df[
            df["CD_SETOR"].notna()
        ],
        faltantes
    ],
    ignore_index=True
)


# ------------------------------------------------------------
# Resumo
# ------------------------------------------------------------

print("\n")
print("="*60)
print("RESULTADO FINAL")
print("="*60)


print(
    df_final["metodo_setor"]
    .value_counts(dropna=False)
)


print(
    "\nSetores:",
    df_final["CD_SETOR"]
    .notna()
    .sum()
)


print(
    "Percentual:",
    round(
        df_final["CD_SETOR"]
        .notna()
        .mean()
        *100,
        2
    ),
    "%"
)


# ------------------------------------------------------------
# Salvar
# ------------------------------------------------------------

df_final.to_csv(
    SAIDA,
    index=False,
    encoding="utf-8-sig"
)


print("\nArquivo salvo:")
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