# ============================================================
# 90_1_auditoria_setores_consumo.py
#
# AUDITORIA DA BASE CONSUMO x SETORES
#
# Objetivo:
# verificar se a associação espacial está consistente antes
# do cálculo de litros/habitante/dia.
#
# ============================================================

import os
import time
import warnings

import pandas as pd

warnings.filterwarnings("ignore")

inicio = time.time()

print("="*70)
print("AUDITORIA DOS SETORES DA BASE DE CONSUMO")
print("="*70)

RESULTADOS = "resultados"

arquivo = os.path.join(
    RESULTADOS,
    "matricula_setor_qgis.csv"
)

if not os.path.exists(arquivo):
    raise Exception(
        f"Arquivo não encontrado:\n{arquivo}"
    )

print("\nLendo base...")

df = pd.read_csv(
    arquivo,
    encoding="utf-8-sig",
    low_memory=False
)

print("Registros:", len(df))

print("\nColunas:")

for c in df.columns:
    print("-", c)

# ============================================================
# IDENTIFICAR CAMPO SETOR
# ============================================================

campo_setor = None

for c in [
    "CD_SETOR_FINAL",
    "CD_SETOR"
]:
    if c in df.columns:
        campo_setor = c
        break

if campo_setor is None:
    raise Exception(
        "Campo de setor não encontrado."
    )

print("\nCampo setor:", campo_setor)

df[campo_setor] = (
    df[campo_setor]
    .astype(str)
    .str.replace(".0", "", regex=False)
    .str.strip()
)

# remover vazios

df.loc[
    df[campo_setor].isin(
        [
            "",
            "nan",
            "None"
        ]
    ),
    campo_setor
] = pd.NA

# ============================================================
# ESTATÍSTICAS GERAIS
# ============================================================

print("\n==============================")
print("ESTATÍSTICAS")
print("==============================")

print("\nRegistros:")
print(len(df))

print("\nCom setor:")
print(df[campo_setor].notna().sum())

print("\nSem setor:")
print(df[campo_setor].isna().sum())

print("\nSetores únicos:")
print(df[campo_setor].nunique())

if "Bairro" in df.columns:

    print("\nBairros únicos:")
    print(df["Bairro"].nunique())

if "BLOCO_3" in df.columns:

    print("\nBlocos 3 únicos:")
    print(df["BLOCO_3"].nunique())

# ============================================================
# DISTRIBUIÇÃO DOS SETORES
# ============================================================

print("\n==============================")
print("TOP 50 SETORES")
print("==============================")

top_setores = (
    df[campo_setor]
    .value_counts(dropna=False)
    .reset_index()
)

top_setores.columns = [
    "CD_SETOR",
    "MATRICULAS"
]

print(top_setores.head(50))

# ============================================================
# SETORES POR BLOCO
# ============================================================

if "BLOCO_3" in df.columns:

    print("\n==============================")
    print("SETORES POR BLOCO_3")
    print("==============================")

    resumo = (
        df.groupby("BLOCO_3")[campo_setor]
        .nunique()
    )

    print(resumo.describe())

    resumo.to_excel(
        os.path.join(
            RESULTADOS,
            "auditoria_setores_por_bloco.xlsx"
        )
    )

# ============================================================
# BLOCOS POR SETOR
# ============================================================

if "BLOCO_3" in df.columns:

    print("\n==============================")
    print("BLOCOS POR SETOR")
    print("==============================")

    resumo2 = (
        df.groupby(campo_setor)["BLOCO_3"]
        .nunique()
    )

    print(resumo2.describe())

    resumo2.to_excel(
        os.path.join(
            RESULTADOS,
            "auditoria_blocos_por_setor.xlsx"
        )
    )

# ============================================================
# BAIRROS POR SETOR
# ============================================================

if "Bairro" in df.columns:

    print("\n==============================")
    print("BAIRROS POR SETOR")
    print("==============================")

    bairros = (
        df.groupby(campo_setor)["Bairro"]
        .nunique()
    )

    print(bairros.describe())

    bairros.to_excel(
        os.path.join(
            RESULTADOS,
            "auditoria_bairros_por_setor.xlsx"
        )
    )

# ============================================================
# PROCURAR POPULAÇÃO
# ============================================================

print("\n==============================")
print("POPULAÇÃO IBGE")
print("==============================")

possiveis = [

    "populacao_setores_ibge.xlsx",

    "populacao_setores.xlsx",

    "populacao_ibge.xlsx",

    "populacao.csv",

    os.path.join(
        RESULTADOS,
        "populacao_setores_ibge.xlsx"
    )
]

achou = False

for arq in possiveis:

    if os.path.exists(arq):

        print("Arquivo encontrado:")

        print(arq)

        achou = True

        break

if not achou:

    print("\n*** ATENÇÃO ***")

    print(
        "Nenhum arquivo de população foi localizado."
    )

    print(
        "O cálculo de litros/habitante/dia ainda não poderá ser realizado."
    )

# ============================================================
# EXPORTAR
# ============================================================

top_setores.to_excel(

    os.path.join(

        RESULTADOS,

        "distribuicao_setores.xlsx"

    ),

    index=False

)

print("\nArquivo criado:")

print(
    "distribuicao_setores.xlsx"
)

print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)

print("\nFim da auditoria.")