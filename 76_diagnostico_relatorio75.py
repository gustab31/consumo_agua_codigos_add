# ============================================================
# 76_diagnostico_relatorio75.py
#
# Diagnóstico do Relatório 75
#
# Objetivo:
# descobrir quais campos permitem ligar:
# matrícula/endereço -> setor censitário
#
# ============================================================

import os
import pandas as pd
import time
import warnings

warnings.filterwarnings("ignore")

inicio = time.time()


print("="*70)
print("DIAGNÓSTICO RELATÓRIO 75")
print("="*70)


ARQUIVO = "2022.06.29. relatorio 75 1.xlsx"

RESULTADOS = "resultados"

os.makedirs(
    RESULTADOS,
    exist_ok=True
)


# ============================================================
# LER PLANILHA
# ============================================================

print("\nLendo arquivo...")

xls = pd.ExcelFile(
    ARQUIVO
)

print("\nAbas:")

for aba in xls.sheet_names:

    print("-", aba)



df = pd.read_excel(

    ARQUIVO,

    sheet_name=xls.sheet_names[0]

)


print("\nShape:")
print(df.shape)



print("\nColunas:")

for c in df.columns:

    print(
        "-",
        c
    )



# ============================================================
# DIAGNÓSTICO DAS COLUNAS
# ============================================================

diagnostico = []


for c in df.columns:


    diagnostico.append({

        "coluna": c,

        "tipo": str(df[c].dtype),

        "valores_unicos": df[c].nunique(),

        "vazios": df[c].isna().sum(),

        "exemplo_1": str(df[c].dropna().iloc[0])
        if df[c].notna().any()
        else ""

    })



diag = pd.DataFrame(
    diagnostico
)



diag.to_excel(

    os.path.join(

        RESULTADOS,

        "diagnostico_colunas_relatorio75.xlsx"

    ),

    index=False

)



# ============================================================
# AMOSTRA
# ============================================================


df.head(200).to_excel(

    os.path.join(

        RESULTADOS,

        "amostra_relatorio75.xlsx"

    ),

    index=False

)



print("\nArquivos gerados:")

print(
    "diagnostico_colunas_relatorio75.xlsx"
)

print(
    "amostra_relatorio75.xlsx"
)


print(

    "\nTempo:",

    round(time.time()-inicio,2),

    "segundos"

)


print("\nFim.")