# ============================================================
# RECUPERAR CD_SETOR FINAL - V15
# ============================================================

import pandas as pd
import os
import re
import unicodedata
import time

inicio = time.time()

print("="*60)
print("RECUPERANDO CD_SETOR FINAL")
print("="*60)


# ------------------------------------------------------------
# arquivos
# ------------------------------------------------------------

arquivo_base = "resultados/base_residencial_p99.csv"

arquivo_espacial = "resultados/base_geocodificada.csv"


# ------------------------------------------------------------
# funções
# ------------------------------------------------------------

def limpar_texto(x):

    if pd.isna(x):
        return ""

    x = str(x).upper()

    x = unicodedata.normalize(
        "NFKD", x
    ).encode(
        "ASCII",
        "ignore"
    ).decode()

    x = re.sub(
        r'[^A-Z0-9]',
        '',
        x
    )

    return x



def limpar_matricula(x):

    if pd.isna(x):
        return ""

    x = str(x)

    x = re.sub(
        r'\D',
        '',
        x
    )

    return x



# ------------------------------------------------------------
# leitura
# ------------------------------------------------------------

print("\nLendo residencial...")

df = pd.read_csv(
    arquivo_base,
    dtype={
        "MATRICULA":"string",
        "CEP":"string"
    }
)

print(df.shape)


print("\nLendo espacial...")

esp = pd.read_csv(
    arquivo_espacial,
    dtype={
        "matricula":"string",
        "CD_SETOR":"string"
    }
)

print(esp.shape)


# ------------------------------------------------------------
# preparar matrículas
# ------------------------------------------------------------

print("\nPadronizando matrículas...")


df["matricula_key"] = (
    df["MATRICULA"]
    .apply(limpar_matricula)
)


esp["matricula_key"] = (
    esp["matricula"]
    .apply(limpar_matricula)
)


# retirar duplicados
esp_mat = (
    esp[
        [
            "matricula_key",
            "CD_SETOR"
        ]
    ]
    .drop_duplicates()
)


print(
    "Espacial matrícula:",
    esp_mat.shape
)


# ------------------------------------------------------------
# merge matrícula
# ------------------------------------------------------------

print("\nMerge matrícula...")


df = df.merge(
    esp_mat,
    on="matricula_key",
    how="left"
)


df["metodo_setor"] = ""

df.loc[
    df["CD_SETOR"].notna(),
    "metodo_setor"
] = "matricula"



# ------------------------------------------------------------
# endereço + bairro
# ------------------------------------------------------------


faltantes = df[
    df["CD_SETOR"].isna()
].copy()


print(
    "\nSem setor:",
    len(faltantes)
)



if len(faltantes)>0:


    print(
        "Tentando endereço + bairro..."
    )


    df["end_key"] = (
        df["Endereco"]
        .apply(limpar_texto)
    )

    df["bairro_key"] = (
        df["Bairro"]
        .apply(limpar_texto)
    )


    esp["end_key"] = (
        esp["endereco"]
        .apply(limpar_texto)
    )

    esp["bairro_key"] = (
        esp["bairro"]
        .apply(limpar_texto)
    )


    esp_end = (
        esp[
            [
                "end_key",
                "bairro_key",
                "CD_SETOR"
            ]
        ]
        .dropna(
            subset=["CD_SETOR"]
        )
        .drop_duplicates()
    )


    df = df.merge(
        esp_end,
        on=[
            "end_key",
            "bairro_key"
        ],
        how="left",
        suffixes=("","_end")
    )


    mask = (
        df["CD_SETOR"]
        .isna()
        &
        df["CD_SETOR_end"]
        .notna()
    )


    df.loc[
        mask,
        "CD_SETOR"
    ] = df.loc[
        mask,
        "CD_SETOR_end"
    ]


    df.loc[
        mask,
        "metodo_setor"
    ] = "endereco_bairro"



    df.drop(
        columns=[
            "CD_SETOR_end"
        ],
        inplace=True
    )



# ------------------------------------------------------------
# limpeza final
# ------------------------------------------------------------


df["CD_SETOR"] = (
    df["CD_SETOR"]
    .astype("string")
)



print("\n")
print("="*40)
print("RESULTADO")
print("="*40)


print(
    df["metodo_setor"]
    .value_counts()
)


print(
    "\nSetores:",
    df["CD_SETOR"]
    .nunique()
)


print(
    "\nPercentual:",
    round(
        df["CD_SETOR"]
        .notna()
        .mean()*100,
        2
    ),
    "%"
)


# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

saida = (
    "resultados/"
    "base_residencial_setor_final.csv"
)


df.to_csv(
    saida,
    index=False,
    encoding="utf-8-sig"
)


print("\nArquivo salvo:")
print(saida)


print("\nTempo:")
print(round(time.time()-inicio,2))

print("\nFim")