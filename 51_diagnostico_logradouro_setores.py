# ============================================================
# 51_diagnostico_logradouro_setores.py
#
# Diagnóstico:
# Quantos setores diferentes existem por logradouro padronizado
# ============================================================

import pandas as pd
import re
import unicodedata
import time
import os

inicio = time.time()

print("="*70)
print("DIAGNÓSTICO DE LOGRADOURO x SETORES")
print("="*70)

ENTRADA = (
    "resultados/"
    "base_residencial_setor_logradouro_normalizado_v3.csv"
)

PASTA = "resultados"

SAIDA1 = (
    PASTA +
    "/diagnostico_logradouro_setores.csv"
)

SAIDA2 = (
    PASTA +
    "/resumo_logradouro_setores.csv"
)

os.makedirs(PASTA, exist_ok=True)

print("\nLendo base...")

df = pd.read_csv(
    ENTRADA,
    low_memory=False
)

print("Shape:", df.shape)

# ============================================================
# Apenas registros COM setor
# ============================================================

df = df[df["CD_SETOR"].notna()].copy()

print("Registros com setor:", len(df))

# ============================================================
# Normalização igual ao Script 50
# ============================================================

def remover_acentos(txt):

    txt = unicodedata.normalize("NFKD", txt)

    txt = txt.encode("ASCII","ignore").decode()

    return txt


def limpar(txt):

    if pd.isna(txt):
        return ""

    txt = str(txt).upper()

    txt = remover_acentos(txt)

    txt = re.sub(r"\(.*?\)", " ", txt)

    txt = re.sub(r"\bS/?N\b", " ", txt)

    txt = re.sub(r",?\s*\d+[A-Z]?$", " ", txt)

    txt = re.sub(r"\bLAT\.?\b", " ", txt)

    txt = re.sub(r"LATERAL DA", " ", txt)

    txt = re.sub(r"LATERAL DO", " ", txt)

    txt = re.sub(r"LATERAL", " ", txt)

    txt = re.sub(r"ACESSO A", " ", txt)

    txt = re.sub(r"FUNDOS", " ", txt)

    txt = re.sub(r"FRENTE", " ", txt)

    txt = re.sub(r"PROXIMO A", " ", txt)

    txt = re.sub(r"\bSD\s*\d+\b", " ", txt)

    txt = re.sub(r"\bRUA\s+\d+\s*-", "", txt)

    txt = txt.replace("ROD.", "RODOVIA")
    txt = txt.replace("EST.", "ESTRADA")
    txt = txt.replace("SERV.", "SERVIDAO")
    txt = txt.replace("AV.", "AVENIDA")

    txt = re.sub(r"\s+", " ", txt)

    return txt.strip()


print("\nPadronizando logradouros...")

df["LOGRADOURO_PAD"] = (
    df["Endereco"]
    .apply(limpar)
)

# ============================================================
# Quantos setores diferentes por logradouro
# ============================================================

diag = (

    df

    .groupby("LOGRADOURO_PAD")

    .agg(

        registros=("CD_SETOR","size"),

        setores_diferentes=("CD_SETOR","nunique")

    )

    .reset_index()

)

diag = diag.sort_values(

    ["setores_diferentes","registros"],

    ascending=[False,False]

)

# ============================================================
# Resumo
# ============================================================

resumo = pd.DataFrame({

    "categoria":[

        "1 setor",

        "2 setores",

        "3 setores",

        "4-5 setores",

        "6-10 setores",

        ">10 setores"

    ],

    "quantidade":[

        (diag["setores_diferentes"]==1).sum(),

        (diag["setores_diferentes"]==2).sum(),

        (diag["setores_diferentes"]==3).sum(),

        ((diag["setores_diferentes"]>=4)&
         (diag["setores_diferentes"]<=5)).sum(),

        ((diag["setores_diferentes"]>=6)&
         (diag["setores_diferentes"]<=10)).sum(),

        (diag["setores_diferentes"]>10).sum()

    ]

})

print("\n")
print("="*70)
print("RESUMO")
print("="*70)

print(resumo)

print("\nTop 30 logradouros mais espalhados:")

print(

    diag.head(30)

)

diag.to_csv(

    SAIDA1,

    index=False,

    encoding="utf-8-sig"

)

resumo.to_csv(

    SAIDA2,

    index=False,

    encoding="utf-8-sig"

)

print("\nArquivos:")

print(SAIDA1)

print(SAIDA2)

print("\nTempo:", round(time.time()-inicio,2),"segundos")

print("\nFim.")