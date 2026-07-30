# ============================================================
# RECUPERAR CD_SETOR POR MATRÍCULA / ENDEREÇO
# ============================================================

import pandas as pd
import os
import time
import unicodedata
import re


inicio = time.time()

print("="*60)
print("RECUPERANDO CD_SETOR POR ENDEREÇO")
print("="*60)


# ============================================================
# ARQUIVOS
# ============================================================

arquivo_base = "resultados/base_residencial_p99.csv"
arquivo_espacial = "resultados/base_geocodificada.csv"

saida = "resultados/base_residencial_com_setor_v2.csv"



# ============================================================
# FUNÇÃO LIMPEZA TEXTO
# ============================================================

def limpar_texto(x):

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
        r"[^A-Z0-9 ]",
        " ",
        x
    )

    x = re.sub(
        r"\s+",
        " ",
        x
    )

    return x.strip()



# ============================================================
# LEITURA
# ============================================================

print("\nLendo base residencial...")

df = pd.read_csv(
    arquivo_base,
    low_memory=False
)

print(df.shape)



print("\nLendo base espacial...")

esp = pd.read_csv(
    arquivo_espacial,
    low_memory=False
)

print(esp.shape)



# ============================================================
# PADRONIZAR MATRÍCULAS
# ============================================================

print("\nPadronizando matrículas...")


df["matricula_test"] = (
    df["MATRICULA"]
    .astype(str)
    .str.replace("-", "", regex=False)
    .str.strip()
)


esp["matricula_test"] = (
    esp["matricula"]
    .astype(str)
    .str.replace("-", "", regex=False)
    .str.strip()
)



# ============================================================
# PREPARAR ESPACIAL
# ============================================================

esp = esp[
    [
        "matricula_test",
        "CD_SETOR",
        "endereco",
        "bairro"
    ]
].copy()


esp = esp.drop_duplicates(
    subset="matricula_test"
)


print(
    "Espacial única:",
    esp.shape
)



# ============================================================
# CRIA COLUNAS AUXILIARES
# ============================================================


df["endereco_limpo"] = df["Endereco"].apply(
    limpar_texto
)

df["bairro_limpo"] = df["Bairro"].apply(
    limpar_texto
)


esp["endereco_limpo"] = esp["endereco"].apply(
    limpar_texto
)

esp["bairro_limpo"] = esp["bairro"].apply(
    limpar_texto
)



# ============================================================
# MERGE 1 - MATRÍCULA
# ============================================================

print("\nMerge por matrícula...")


map_matricula = (
    esp[
        [
            "matricula_test",
            "CD_SETOR"
        ]
    ]
    .drop_duplicates()
)


df = df.merge(
    map_matricula,
    on="matricula_test",
    how="left"
)


df["metodo_setor"] = "nao_encontrado"


df.loc[
    df["CD_SETOR"].notna(),
    "metodo_setor"
] = "matricula"



# ============================================================
# MERGE 2 - ENDEREÇO + BAIRRO
# ============================================================

print("\nTentando endereço + bairro...")


faltantes = df[
    df["CD_SETOR"].isna()
].copy()


map_end = (
    esp[
        [
            "endereco_limpo",
            "bairro_limpo",
            "CD_SETOR"
        ]
    ]
    .dropna(subset=["CD_SETOR"])
    .drop_duplicates(
        [
            "endereco_limpo",
            "bairro_limpo"
        ]
    )
)


faltantes = faltantes.merge(
    map_end,
    on=[
        "endereco_limpo",
        "bairro_limpo"
    ],
    how="left"
)


if "CD_SETOR_y" in faltantes.columns:

    idx = df["CD_SETOR"].isna()

    df.loc[
        idx,
        "CD_SETOR"
    ] = faltantes["CD_SETOR_y"].values


    df.loc[
        idx & df["CD_SETOR"].notna(),
        "metodo_setor"
    ] = "endereco_bairro"

else:

    print(
        "Nenhum setor encontrado por endereço+bairro"
    )



# ============================================================
# MERGE 3 - ENDEREÇO
# ============================================================

print("\nTentando endereço...")


faltantes = df[
    df["CD_SETOR"].isna()
].copy()


map_endereco = (
    esp[
        [
            "endereco_limpo",
            "CD_SETOR"
        ]
    ]
    .dropna(subset=["CD_SETOR"])
    .drop_duplicates(
        "endereco_limpo"
    )
)



faltantes = faltantes.merge(
    map_endereco,
    on="endereco_limpo",
    how="left"
)


if "CD_SETOR_y" in faltantes.columns:

    idx = df["CD_SETOR"].isna()


    df.loc[
        idx,
        "CD_SETOR"
    ] = faltantes["CD_SETOR_y"].values


    df.loc[
        idx & df["CD_SETOR"].notna(),
        "metodo_setor"
    ] = "endereco"

else:

    print(
        "Nenhum setor encontrado por endereço"
    )



# ============================================================
# LIMPEZA FINAL
# ============================================================

df = df.drop(
    columns=[
        "matricula_test",
        "endereco_limpo",
        "bairro_limpo"
    ],
    errors="ignore"
)



# ============================================================
# RESULTADO
# ============================================================

print("\n")
print("="*40)
print("RESULTADO FINAL")
print("="*40)


print("\nMétodos:")
print(
    df["metodo_setor"]
    .value_counts()
)



print("\nSetores encontrados:")

print(
    df["CD_SETOR"]
    .notna()
    .sum()
)



print("\nPercentual com setor:")

print(
    round(
        df["CD_SETOR"]
        .notna()
        .mean()
        *100,
        2
    ),
    "%"
)



print("\nNulos:")
print(
    df["CD_SETOR"]
    .isna()
    .sum()
)



# ============================================================
# SALVAR
# ============================================================

df.to_csv(
    saida,
    index=False,
    encoding="utf-8-sig"
)


print("\nArquivo salvo:")
print(saida)


print("\nTempo:")
print(
    round(
        time.time()-inicio,
        2
    ),
    "segundos"
)


print("\nFim")