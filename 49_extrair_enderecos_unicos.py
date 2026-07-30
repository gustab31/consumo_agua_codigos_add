# ============================================================
# 49_extrair_enderecos_unicos.py
#
# Extrai endereços únicos para geocodificação
# ============================================================

import pandas as pd
import os
import time

inicio = time.time()

print("="*70)
print("EXTRAÇÃO DE ENDEREÇOS ÚNICOS")
print("="*70)

ENTRADA = (
    "resultados/"
    "base_residencial_setor_logradouro_normalizado_v3.csv"
)

PASTA = "resultados"

SAIDA = (
    PASTA +
    "/enderecos_unicos_para_geocodificar.csv"
)

os.makedirs(PASTA, exist_ok=True)

print("\nLendo base...")

df = pd.read_csv(
    ENTRADA,
    low_memory=False
)

print("Shape:", df.shape)

# ------------------------------------------------------------
# garante colunas
# ------------------------------------------------------------

for c in ["Endereco","Bairro","CEP","CD_SETOR"]:

    if c not in df.columns:
        df[c] = ""

df["Endereco"] = (
    df["Endereco"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["Bairro"] = (
    df["Bairro"]
    .fillna("")
    .astype(str)
    .str.strip()
)

df["CEP"] = (
    df["CEP"]
    .fillna("")
    .astype(str)
    .str.strip()
)

# ------------------------------------------------------------
# apenas registros sem setor
# ------------------------------------------------------------

sem = df[
    (df["CD_SETOR"].isna()) |
    (df["CD_SETOR"]=="")
].copy()

print("\nSem setor:", len(sem))

# ------------------------------------------------------------
# cria chave
# ------------------------------------------------------------

sem["CHAVE"] = (

    sem["Endereco"]
    + " | "
    + sem["Bairro"]
    + " | "
    + sem["CEP"]

)

# ------------------------------------------------------------
# quantidade por endereço
# ------------------------------------------------------------

unicos = (

    sem
    .groupby(
        ["Endereco","Bairro","CEP"]
    )
    .size()
    .reset_index(name="matriculas")

)

unicos = unicos.sort_values(
    "matriculas",
    ascending=False
)

# ------------------------------------------------------------
# colunas para geocodificação
# ------------------------------------------------------------

unicos["municipio"] = "Joinville"

unicos["estado"] = "SC"

unicos["pais"] = "Brasil"

unicos["latitude"] = ""

unicos["longitude"] = ""

unicos["status"] = ""

unicos["fonte"] = ""

# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

unicos.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)

print("\n")

print("="*70)

print("RESULTADO")

print("="*70)

print("Matrículas sem setor :", len(sem))

print("Endereços únicos :", len(unicos))

print("\nTop 20:")

print(unicos.head(20))

print("\nArquivo:")

print(SAIDA)

print("\nTempo:", round(time.time()-inicio,2),"segundos")

print("\nFim.")