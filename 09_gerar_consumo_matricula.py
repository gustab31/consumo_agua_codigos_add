# =====================================================
# 09_gerar_consumo_matricula.py
# =====================================================

import pandas as pd
import os
import time


inicio = time.time()


print("="*60)
print("GERAÇÃO DO CONSUMO MÉDIO POR MATRÍCULA")
print("="*60)


# =====================================================
# ARQUIVOS
# =====================================================

arquivos = [
    "fev20 a mar22.csv",
    "abr22 a maio24.csv"
]


saida = (
    "resultados/consumo_matricula.csv"
)


os.makedirs(
    "resultados",
    exist_ok=True
)



# =====================================================
# LEITURA DOS ARQUIVOS
# =====================================================

bases = []


for arquivo in arquivos:


    print("\nLendo:")
    print(arquivo)


    if not os.path.exists(arquivo):

        raise FileNotFoundError(
            f"Arquivo não encontrado: {arquivo}"
        )


    df = pd.read_csv(
        arquivo,
        encoding="latin1",
        sep=";",
        low_memory=False
    )


    # limpar nomes

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.upper()
    )


    print("\nColunas:")
    print(df.columns.tolist())


    if "MATRICULA" not in df.columns:

        raise ValueError(
            "Coluna MATRICULA não encontrada"
        )



    # remover linha "mês"

    primeira = (
        str(df.iloc[0]["MATRICULA"])
        .strip()
        .lower()
    )


    if primeira == "mês":

        df = df.iloc[1:].copy()



    # matrícula

    df["MATRICULA"] = (
        df["MATRICULA"]
        .astype(str)
        .str.strip()
    )



    # identificar meses

    colunas_mes = [
        c for c in df.columns
        if "MICROMEDIDO" in c
    ]


    print(
        "\nQuantidade meses:",
        len(colunas_mes)
    )



    # =================================================
    # LIMPEZA DOS CONSUMOS
    # =================================================


    for c in colunas_mes:


        df[c] = (
            df[c]
            .astype(str)
            .str.replace(
                ",",
                ".",
                regex=False
            )
        )


        df[c] = pd.to_numeric(
            df[c],
            errors="coerce"
        )



    # remover valores impossíveis

    df[colunas_mes] = df[colunas_mes].mask(
        (df[colunas_mes] < 0) |
        (df[colunas_mes] > 10000)
    )



    # média do período

    df["CONSUMO_MEDIO_M3"] = (
        df[colunas_mes]
        .mean(axis=1)
    )



    # guardar apenas necessário

    bases.append(
        df[
            [
                "MATRICULA",
                "CONSUMO_MEDIO_M3"
            ]
        ]
    )



# =====================================================
# JUNTAR OS DOIS PERÍODOS
# =====================================================

print("\nJuntando períodos...")


consumo = pd.concat(
    bases,
    ignore_index=True
)



print(
    "\nRegistros totais:",
    len(consumo)
)



# =====================================================
# LIMPEZA FINAL
# =====================================================


consumo = consumo.dropna(
    subset=[
        "MATRICULA",
        "CONSUMO_MEDIO_M3"
    ]
)


consumo = consumo[
    (consumo["CONSUMO_MEDIO_M3"] >= 0) &
    (consumo["CONSUMO_MEDIO_M3"] <= 10000)
]



print(
    "\nRegistros após limpeza:",
    len(consumo)
)



# =====================================================
# MÉDIA FINAL POR MATRÍCULA
# =====================================================


consumo_final = (
    consumo
    .groupby("MATRICULA")
    ["CONSUMO_MEDIO_M3"]
    .mean()
    .reset_index()
)



consumo_final = consumo_final.rename(
    columns={
        "CONSUMO_MEDIO_M3":
        "consumo_medio_m3"
    }
)



# =====================================================
# DIAGNÓSTICO
# =====================================================


print("\n==============================")
print("RESUMO FINAL")
print("==============================")


print(
    consumo_final[
        "consumo_medio_m3"
    ]
    .describe()
)



print(
    "\nMatrículas únicas:"
)

print(
    consumo_final["MATRICULA"]
    .nunique()
)



print(
    "\nMaiores consumos:"
)


print(
    consumo_final
    .sort_values(
        "consumo_medio_m3",
        ascending=False
    )
    .head(10)
)



# =====================================================
# EXPORTAÇÃO
# =====================================================


consumo_final.to_csv(
    saida,
    index=False,
    encoding="utf-8-sig"
)



print("\nArquivo salvo:")
print(saida)



print("\nTempo total:")

print(
    round(
        time.time()-inicio,
        2
    ),
    "segundos"
)


print("\nProcessamento concluído.")