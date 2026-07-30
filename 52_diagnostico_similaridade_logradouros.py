# ============================================================
# 52_diagnostico_similaridade_logradouros.py
#
# Descobre logradouros praticamente iguais
# que impedem a propagação de CD_SETOR
# ============================================================

import pandas as pd
import re
import unicodedata
import time
import os

from rapidfuzz import process, fuzz

inicio = time.time()

print("="*70)
print("DIAGNÓSTICO DE SIMILARIDADE ENTRE LOGRADOUROS")
print("="*70)

ENTRADA = (
    "resultados/"
    "base_residencial_setor_logradouro_normalizado_v3.csv"
)

PASTA = "resultados"

ARQUIVO = (
    PASTA +
    "/diagnostico_similaridade_logradouros.csv"
)

os.makedirs(PASTA, exist_ok=True)

print("\nLendo base...")

df = pd.read_csv(
    ENTRADA,
    low_memory=False
)

# ------------------------------------------------------------
# normalização
# ------------------------------------------------------------

def remover(txt):

    txt = unicodedata.normalize(
        "NFKD",
        txt
    )

    txt = (
        txt
        .encode("ASCII","ignore")
        .decode()
    )

    return txt


def limpar(txt):

    if pd.isna(txt):
        return ""

    txt = str(txt).upper()

    txt = remover(txt)

    txt = re.sub(r"\(.*?\)", " ", txt)

    txt = re.sub(r"\bS/?N\b", " ", txt)

    txt = re.sub(r",?\s*\d+[A-Z]?$", " ", txt)

    txt = re.sub(r"[^A-Z ]"," ",txt)

    txt = re.sub(r"\s+"," ",txt)

    return txt.strip()

print("\nNormalizando...")

df["LOGRADOURO"] = (
    df["Endereco"]
    .apply(limpar)
)

# ------------------------------------------------------------
# conhecidos
# ------------------------------------------------------------

conhecidos = sorted(

    df.loc[
        df["CD_SETOR"].notna(),
        "LOGRADOURO"
    ].unique()

)

# ------------------------------------------------------------
# desconhecidos
# ------------------------------------------------------------

desconhecidos = sorted(

    df.loc[
        df["CD_SETOR"].isna(),
        "LOGRADOURO"
    ].unique()

)

print("\nCom setor :",len(conhecidos))
print("Sem setor :",len(desconhecidos))

# ------------------------------------------------------------
# comparação
# ------------------------------------------------------------

resultado=[]

print("\nComparando...")

for i,rua in enumerate(desconhecidos):

    if len(rua)<6:
        continue

    achou = process.extractOne(

        rua,

        conhecidos,

        scorer=fuzz.token_sort_ratio

    )

    if achou is None:
        continue

    melhor,score,_ = achou

    if score>=90:

        resultado.append({

            "logradouro_sem_setor":rua,

            "logradouro_conhecido":melhor,

            "similaridade":score

        })

    if i%500==0:

        print(i,"/",len(desconhecidos))

# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

resultado=pd.DataFrame(resultado)

resultado=resultado.sort_values(

    "similaridade",

    ascending=False

)

resultado.to_csv(

    ARQUIVO,

    index=False,

    encoding="utf-8-sig"

)

print("\n")
print("="*70)
print("RESULTADO")
print("="*70)

print("Correspondências:",len(resultado))

print("\nTop 40:")

print(resultado.head(40))

print("\nArquivo:")

print(ARQUIVO)

print("\nTempo:",round(time.time()-inicio,2),"segundos")

print("\nFim.")