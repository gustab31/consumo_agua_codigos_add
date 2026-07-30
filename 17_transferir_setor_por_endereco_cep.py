# ============================================================
# TRANSFERIR CD_SETOR POR ENDEREÇO + CEP - V3
# CORREÇÃO DUPLICIDADE CD_SETOR_NOVO
# ============================================================

import pandas as pd
import os
import re
import unicodedata
import time


inicio = time.time()

print("="*60)
print("TRANSFERINDO CD_SETOR POR ENDEREÇO + CEP - V3")
print("="*60)



# ============================================================
# ARQUIVOS
# ============================================================

BASE = "resultados/base_residencial_setor_endereco.csv"

ESPACIAL = [
    "resultados/base_geocodificada.csv",
    "resultados/base_final_espacial.csv"
]

SAIDA = "resultados/base_residencial_setor_endereco_cep_v3.csv"



# ============================================================
# FUNÇÃO NORMALIZAÇÃO
# ============================================================

def normalizar(x):

    if pd.isna(x):
        return ""

    x = str(x).upper()

    x = unicodedata.normalize(
        "NFKD",
        x
    ).encode(
        "ASCII",
        "ignore"
    ).decode(
        "ASCII"
    )

    x = re.sub(
        r"[^A-Z0-9]",
        "",
        x
    )

    return x



# ============================================================
# LEITURA
# ============================================================

print("\nLendo residencial...")

df = pd.read_csv(
    BASE,
    low_memory=False
)

print(df.shape)



# LIMPA COLUNAS DE EXECUÇÕES ANTERIORES

remover = [
    c for c in df.columns
    if (
        "NOVO" in c
        or
        "AUX" in c
        or
        c in [
            "CD_SETOR_CEP",
            "CHAVE_END_CEP"
        ]
    )
]


if remover:

    print(
        "Removendo colunas antigas:",
        remover
    )

    df.drop(
        columns=remover,
        inplace=True
    )



if "CD_SETOR" not in df.columns:
    df["CD_SETOR"] = None


if "metodo_setor" not in df.columns:
    df["metodo_setor"] = ""


if "confianca" not in df.columns:
    df["confianca"] = ""



# ============================================================
# BUSCAR SETORES CONHECIDOS
# ============================================================

bases = []


for arq in ESPACIAL:

    if os.path.exists(arq):

        print("\nEncontrado:")
        print(arq)

        temp = pd.read_csv(
            arq,
            low_memory=False
        )


        if (
            "matricula" in temp.columns
            and
            "CD_SETOR" in temp.columns
        ):

            temp = temp[
                [
                    "matricula",
                    "CD_SETOR"
                ]
            ]


            temp.columns = [
                "MATRICULA",
                "CD_SETOR_REF"
            ]


            bases.append(temp)



setores = pd.concat(
    bases,
    ignore_index=True
)



setores["MATRICULA"] = (
    setores["MATRICULA"]
    .astype(str)
)



setores = setores.drop_duplicates()



print(
    "\nSetores disponíveis:",
    setores.shape
)



# ============================================================
# TRANSFERÊNCIA MATRÍCULA
# ============================================================


print("\nTransferindo por matrícula...")


df["MATRICULA"] = (
    df["MATRICULA"]
    .astype(str)
)



# IMPORTANTE:
# não usar suffix automático

df = df.merge(
    setores,
    on="MATRICULA",
    how="left"
)



mask = (
    df["CD_SETOR"].isna()
    &
    df["CD_SETOR_REF"].notna()
)



df.loc[
    mask,
    "CD_SETOR"
] = df.loc[
    mask,
    "CD_SETOR_REF"
]


df.loc[
    mask,
    "metodo_setor"
] = "matricula"


df.loc[
    mask,
    "confianca"
] = "alta"



df.drop(
    columns=[
        "CD_SETOR_REF"
    ],
    inplace=True
)



print(
    "Por matrícula:",
    mask.sum()
)



# ============================================================
# CHAVE ENDEREÇO CEP
# ============================================================

print("\nCriando chave endereço...")


df["CHAVE_END_CEP"] = (

    df["Endereco"]
    .fillna("")
    .apply(normalizar)

    +

    "_"

    +

    df["CEP"]
    .fillna("")
    .astype(str)
    .apply(normalizar)

)



# ============================================================
# MAPA DE ENDEREÇOS CONFIÁVEIS
# ============================================================


print("\nCriando mapa endereço...")


controle = (

    df[
        df["CD_SETOR"].notna()
    ]

    .groupby(
        "CHAVE_END_CEP"
    )
    [
        "CD_SETOR"
    ]
    .nunique()

)



validos = controle[
    controle == 1
].index



mapa = (

    df[
        df["CHAVE_END_CEP"]
        .isin(validos)
    ]

    [
        [
            "CHAVE_END_CEP",
            "CD_SETOR"
        ]
    ]

    .drop_duplicates()

)



mapa = mapa.rename(
    columns={
        "CD_SETOR":
        "SETOR_END_REF"
    }
)



print(
    "Endereços confiáveis:",
    len(mapa)
)



# ============================================================
# TRANSFERÊNCIA ENDEREÇO
# ============================================================


print("\nTransferindo endereço...")


df = df.merge(
    mapa,
    on="CHAVE_END_CEP",
    how="left"
)



mask = (

    df["CD_SETOR"].isna()

    &

    df["SETOR_END_REF"].notna()

)



df.loc[
    mask,
    "CD_SETOR"
] = df.loc[
    mask,
    "SETOR_END_REF"
]


df.loc[
    mask,
    "metodo_setor"
] = "endereco_cep"


df.loc[
    mask,
    "confianca"
] = "alta"



df.drop(
    columns=[
        "SETOR_END_REF"
    ],
    inplace=True
)



# ============================================================
# RESULTADO
# ============================================================


print("\n")
print("="*60)
print("RESULTADO FINAL")
print("="*60)


print(
    df["metodo_setor"]
    .value_counts(dropna=False)
)


print(
    "\nSetores:",
    df["CD_SETOR"]
    .notna()
    .sum()
)


print(
    "Percentual:",
    round(
        df["CD_SETOR"]
        .notna()
        .mean()
        *100,
        2
    ),
    "%"
)



# ============================================================
# SALVAR
# ============================================================


df.to_csv(
    SAIDA,
    index=False,
    encoding="utf-8-sig"
)


print("\nSalvo:")
print(SAIDA)


print(
    "\nTempo:",
    round(
        time.time()-inicio,
        2
    ),
    "segundos"
)


print("\nFim.")