# ============================================================
# 20_preparar_geocodificacao_prioridade_alta.py
# ============================================================

import pandas as pd
import time
import os


inicio = time.time()


print("="*60)
print("PREPARANDO GEOCODIFICACAO PRIORIDADE ALTA")
print("="*60)



# ============================================================
# ARQUIVOS
# ============================================================

ENTRADA = (
    "resultados/"
    "fila_geocodificacao_endereco.csv"
)


SAIDA = (
    "resultados/"
    "geocode_prioridade_alta.csv"
)



# ============================================================
# LEITURA
# ============================================================

print("\nLendo fila de endereços...")


df = pd.read_csv(
    ENTRADA,
    low_memory=False
)


print(
    "Shape:",
    df.shape
)



print("\nColunas:")

print(
    df.columns.tolist()
)



# ============================================================
# FILTRAR PRIORIDADE
# ============================================================


print("\nSelecionando prioridades...")


prioridades = [
    "MUITO_ALTA",
    "ALTA"
]


geo = df[
    df["prioridade"]
    .isin(prioridades)
].copy()



# ============================================================
# ORDENAR
# ============================================================


geo = geo.sort_values(
    [
        "prioridade",
        "total_matriculas"
    ],
    ascending=[
        True,
        False
    ]
)



# ============================================================
# RESUMO
# ============================================================


print("\n")
print("="*60)
print("RESUMO DA FILA")
print("="*60)



print(
    "Endereços selecionados:",
    len(geo)
)


print(
    "\nDistribuição:"
)

print(
    geo["prioridade"]
    .value_counts()
)



print(
    "\nMatrículas potencialmente recuperadas:"
)

print(
    geo["total_matriculas"]
    .sum()
)



print(
    "\nLista:"
)

print(

    geo[
        [
            "endereco",
            "bairro",
            "cep",
            "total_matriculas",
            "prioridade"
        ]
    ]

)



# ============================================================
# ADICIONAR CONTROLE
# ============================================================


geo["status_geocode"] = "pendente"

geo["latitude"] = None

geo["longitude"] = None

geo["CD_SETOR"] = None

geo["metodo_setor"] = None

geo["confianca"] = None



# ============================================================
# SALVAR
# ============================================================


geo.to_csv(
    SAIDA,
    index=False,
    encoding="utf-8-sig"
)



print("\nArquivo salvo:")

print(SAIDA)



print("\nTempo:")

print(
    round(
        time.time()-inicio,
        2
    ),
    "segundos"
)



print("\nFim.")