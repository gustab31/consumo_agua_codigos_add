# ============================================================
# 48_diagnostico_qualidade_cadastral.py
#
# Diagnóstico da qualidade cadastral dos registros sem CD_SETOR
# ============================================================

import pandas as pd
import os
import time

inicio = time.time()

print("="*70)
print("DIAGNÓSTICO DA QUALIDADE CADASTRAL")
print("="*70)

# ============================================================
# ARQUIVOS
# ============================================================

ENTRADA = (
    "resultados/"
    "base_residencial_setor_logradouro_normalizado_v3.csv"
)

PASTA = "resultados"

ARQ_RESUMO = (
    PASTA +
    "/resumo_qualidade_cadastral.csv"
)

ARQ_BAIRROS = (
    PASTA +
    "/bairros_sem_setor.csv"
)

ARQ_LOGRADOUROS = (
    PASTA +
    "/logradouros_sem_setor.csv"
)

ARQ_NUMEROS = (
    PASTA +
    "/diagnostico_numeracao.csv"
)

os.makedirs(PASTA, exist_ok=True)

# ============================================================
# LEITURA
# ============================================================

print("\nLendo base...")

df = pd.read_csv(
    ENTRADA,
    low_memory=False
)

print("Shape:", df.shape)

# ============================================================
# GARANTIR COLUNAS
# ============================================================

colunas = [
    "Endereco",
    "Bairro",
    "CEP",
    "CD_SETOR"
]

for c in colunas:

    if c not in df.columns:
        df[c] = ""

# tudo como texto

for c in colunas:

    df[c] = (
        df[c]
        .fillna("")
        .astype(str)
        .str.strip()
    )

# ============================================================
# REGISTROS SEM SETOR
# ============================================================

sem = df[
    (df["CD_SETOR"] == "")
    |
    (df["CD_SETOR"].isna())
].copy()

com = df[
    ~( (df["CD_SETOR"] == "") | (df["CD_SETOR"].isna()) )
].copy()

print("\nCom setor :", len(com))
print("Sem setor :", len(sem))

# ============================================================
# FUNÇÃO PARA EXTRAIR NÚMERO
# ============================================================

def classificar_numero(end):

    end = str(end).upper()

    if end == "":
        return "ENDERECO_VAZIO"

    if "SN" in end or "S/N" in end:
        return "SEM_NUMERO"

    import re

    numeros = re.findall(r"\d+", end)

    if len(numeros) == 0:
        return "SEM_NUMERO"

    return "COM_NUMERO"

sem["TIPO_NUMERO"] = sem["Endereco"].apply(classificar_numero)

# ============================================================
# RESUMO GERAL
# ============================================================

total = len(df)

com_setor = len(com)

sem_setor = len(sem)

bairro_preenchido = (
    sem["Bairro"]
    .ne("")
    .sum()
)

bairro_vazio = (
    sem["Bairro"]
    .eq("")
    .sum()
)

endereco_preenchido = (
    sem["Endereco"]
    .ne("")
    .sum()
)

endereco_vazio = (
    sem["Endereco"]
    .eq("")
    .sum()
)

cep_preenchido = (
    sem["CEP"]
    .ne("")
    .sum()
)

cep_vazio = (
    sem["CEP"]
    .eq("")
    .sum()
)

numero = (
    sem["TIPO_NUMERO"]
    .value_counts()
)

resumo = pd.DataFrame({

    "indicador":[

        "total_registros",

        "com_CD_SETOR",

        "sem_CD_SETOR",

        "percentual_cobertura",

        "bairro_preenchido",

        "bairro_vazio",

        "endereco_preenchido",

        "endereco_vazio",

        "cep_preenchido",

        "cep_vazio",

        "com_numero",

        "sem_numero"

    ],

    "valor":[

        total,

        com_setor,

        sem_setor,

        round(com_setor/total*100,2),

        bairro_preenchido,

        bairro_vazio,

        endereco_preenchido,

        endereco_vazio,

        cep_preenchido,

        cep_vazio,

        numero.get("COM_NUMERO",0),

        numero.get("SEM_NUMERO",0)

    ]

})

# ============================================================
# BAIRROS
# ============================================================

print("\nGerando estatísticas por bairro...")

bairro_total = (
    df
    .groupby("Bairro")
    .size()
    .rename("total")
)

bairro_com = (
    com
    .groupby("Bairro")
    .size()
    .rename("com_setor")
)

bairro_sem = (
    sem
    .groupby("Bairro")
    .size()
    .rename("sem_setor")
)

bairros = (
    pd.concat(
        [
            bairro_total,
            bairro_com,
            bairro_sem
        ],
        axis=1
    )
    .fillna(0)
)

bairros["cobertura_%"] = (
    bairros["com_setor"]
    /
    bairros["total"]
    *100
).round(2)

bairros = bairros.sort_values(
    "sem_setor",
    ascending=False
)

# ============================================================
# LOGRADOUROS
# ============================================================

print("Gerando estatísticas por logradouro...")

logradouro = (
    sem["Endereco"]
    .value_counts()
    .reset_index()
)

logradouro.columns = [

    "Endereco",

    "quantidade_sem_setor"

]

# ============================================================
# NUMERAÇÃO
# ============================================================

numeracao = (
    sem["TIPO_NUMERO"]
    .value_counts()
    .reset_index()
)

numeracao.columns = [

    "tipo",

    "quantidade"

]

# ============================================================
# SALVAR
# ============================================================

print("\nSalvando...")

resumo.to_csv(
    ARQ_RESUMO,
    index=False,
    encoding="utf-8-sig"
)

bairros.to_csv(
    ARQ_BAIRROS,
    encoding="utf-8-sig"
)

logradouro.to_csv(
    ARQ_LOGRADOUROS,
    index=False,
    encoding="utf-8-sig"
)

numeracao.to_csv(
    ARQ_NUMEROS,
    index=False,
    encoding="utf-8-sig"
)

# ============================================================
# RESULTADO
# ============================================================

print("\n")
print("="*70)
print("RESUMO")
print("="*70)

print(resumo)

print("\nTOP 20 BAIRROS COM MAIS REGISTROS SEM SETOR\n")

print(
    bairros.head(20)
)

print("\nTOP 20 LOGRADOUROS SEM SETOR\n")

print(
    logradouro.head(20)
)

print("\nDistribuição da numeração\n")

print(
    numeracao
)

print("\nArquivos gerados:")

print(ARQ_RESUMO)
print(ARQ_BAIRROS)
print(ARQ_LOGRADOUROS)
print(ARQ_NUMEROS)

print("\nTempo:", round(time.time()-inicio,2), "segundos")

print("\nFim.")