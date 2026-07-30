# ============================================================
# 57_analise_confianca_CEP.py
#
# Analise da confiabilidade dos CEPs usados
# na inferência de setor censitário
#
# ============================================================

import os
import time
import pandas as pd


inicio = time.time()


print("="*70)
print("ANÁLISE DE CONFIANÇA DOS CEPs")
print("="*70)


# ------------------------------------------------------------
# arquivos
# ------------------------------------------------------------

ENTRADA = "resultados/base_setor_final_CEP.csv"

SAIDA_CEP = "resultados/analise_confianca_CEP.csv"

SAIDA_RESUMO = "resultados/resumo_confianca_CEP.csv"


# ------------------------------------------------------------
# leitura
# ------------------------------------------------------------

print("\nLendo base...")

df = pd.read_csv(
    ENTRADA,
    low_memory=False
)


print("Registros:")
print(len(df))


# ------------------------------------------------------------
# padronização
# ------------------------------------------------------------

df["CEP"] = (

    df["CEP"]
    .astype("string")
    .str.replace(
        r"\D",
        "",
        regex=True
    )

)


df["CD_SETOR_FINAL"] = (

    df["CD_SETOR_FINAL"]
    .astype("string")

)


# ------------------------------------------------------------
# somente setores atribuídos
# ------------------------------------------------------------

base = df[
    df["CEP"].notna()
    &
    df["CD_SETOR_FINAL"].notna()
].copy()


print("\nRegistros analisados:")
print(len(base))


# ------------------------------------------------------------
# distribuição CEP x setor
# ------------------------------------------------------------

print("\nCalculando dominância dos CEPs...")


cep_setor = (

    base
    .groupby(
        [
            "CEP",
            "CD_SETOR_FINAL"
        ]
    )
    .size()
    .reset_index(
        name="quantidade"
    )

)


total_cep = (

    base
    .groupby(
        "CEP"
    )
    .size()
    .reset_index(
        name="total_CEP"
    )

)


dominante = (

    cep_setor
    .sort_values(
        [
            "CEP",
            "quantidade"
        ],
        ascending=[
            True,
            False
        ]
    )
    .drop_duplicates(
        "CEP"
    )

)


dominante = dominante.merge(
    total_cep,
    on="CEP",
    how="left"
)


dominante["percentual_dominancia"] = (

    dominante["quantidade"]
    /
    dominante["total_CEP"]
    *
    100

)


# ------------------------------------------------------------
# classificação
# ------------------------------------------------------------

def classe(valor):

    if valor >= 95:

        return "ALTA"

    elif valor >= 80:

        return "MEDIA"

    else:

        return "BAIXA"



dominante["classe_confianca"] = (

    dominante["percentual_dominancia"]
    .apply(classe)

)


# ------------------------------------------------------------
# estatísticas
# ------------------------------------------------------------

resumo = (

    dominante["classe_confianca"]
    .value_counts()
    .reset_index()

)


resumo.columns = [

    "classe",

    "quantidade_CEP"

]


print("\n")
print("="*70)
print("RESULTADO")
print("="*70)


print(resumo)


print("\nEstatísticas:")

print(
    dominante[
        [
            "percentual_dominancia"
        ]
    ]
    .describe()
)


# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

os.makedirs(
    "resultados",
    exist_ok=True
)


dominante.to_csv(
    SAIDA_CEP,
    index=False,
    encoding="utf-8-sig"
)


resumo.to_csv(
    SAIDA_RESUMO,
    index=False,
    encoding="utf-8-sig"
)


print("\nArquivos:")

print(SAIDA_CEP)

print(SAIDA_RESUMO)


tempo = round(
    time.time()-inicio,
    2
)


print("\nTempo:")
print(
    tempo,
    "segundos"
)


print("\nFim.")