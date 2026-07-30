# ============================================================
# 55_validacao_regra_CEP.py
#
# Validação da inferência de setor por CEP
#
# ============================================================

import os
import time
import pandas as pd

inicio = time.time()

print("="*70)
print("VALIDAÇÃO DA REGRA DE INFERÊNCIA POR CEP")
print("="*70)


ENTRADA = "resultados/base_inferencia_espacial_setor_v1.csv"

SAIDA = "resultados/validacao_regra_CEP.csv"

RESUMO = "resultados/resumo_validacao_CEP.csv"


# ------------------------------------------------------------
# leitura
# ------------------------------------------------------------

print("\nLendo base...")

df = pd.read_csv(
    ENTRADA,
    low_memory=False
)

print("Registros:", len(df))


# ------------------------------------------------------------
# padronização
# ------------------------------------------------------------

df["CD_SETOR"] = (
    df["CD_SETOR"]
    .astype("string")
    .replace(
        ["", "nan", "None"],
        pd.NA
    )
)


df["CEP"] = (
    df["CEP"]
    .astype("string")
    .str.replace(
        r"\D",
        "",
        regex=True
    )
)


print("\nCom setor:")

print(
    df["CD_SETOR"]
    .notna()
    .sum()
)


# ------------------------------------------------------------
# apenas registros confiáveis
# ------------------------------------------------------------

base = df[
    df["CD_SETOR"].notna()
].copy()


# ------------------------------------------------------------
# separação treino/teste
# ------------------------------------------------------------

teste = base.sample(
    frac=0.20,
    random_state=42
)


treino = base.drop(
    teste.index
)


print("\nAmostra teste:")
print(len(teste))


# ------------------------------------------------------------
# criar regra CEP
# ------------------------------------------------------------

print("\nCriando CEP dominante...")


cep_setor = (

    treino
    .groupby(
        [
            "CEP",
            "CD_SETOR"
        ],
        dropna=False
    )
    .size()
    .reset_index(
        name="quantidade"
    )

)


cep_dominante = (

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
        subset="CEP"
    )

)


cep_dominante = cep_dominante[
    [
        "CEP",
        "CD_SETOR"
    ]
]


cep_dominante = cep_dominante.rename(
    columns={
        "CD_SETOR":
        "CD_SETOR_PREVISTO"
    }
)


print(
    "CEPs modelados:",
    len(cep_dominante)
)


# ------------------------------------------------------------
# aplicar previsão
# ------------------------------------------------------------

teste = teste.merge(
    cep_dominante,
    on="CEP",
    how="left"
)


# ------------------------------------------------------------
# comparação segura
# ------------------------------------------------------------

teste["CD_SETOR_REAL"] = (
    teste["CD_SETOR"]
    .fillna("")
    .astype(str)
)


teste["CD_SETOR_PREVISTO"] = (
    teste["CD_SETOR_PREVISTO"]
    .fillna("")
    .astype(str)
)



def classificar(row):

    if row["CD_SETOR_PREVISTO"] == "":
        return "SEM_PREVISAO"

    elif (
        row["CD_SETOR_PREVISTO"]
        ==
        row["CD_SETOR_REAL"]
    ):
        return "CORRETO"

    else:
        return "ERRO"



teste["resultado"] = teste.apply(
    classificar,
    axis=1
)


# ------------------------------------------------------------
# estatística
# ------------------------------------------------------------

resumo = (

    teste["resultado"]
    .value_counts()
    .reset_index()

)

resumo.columns = [
    "categoria",
    "quantidade"
]


corretos = (
    teste["resultado"]
    ==
    "CORRETO"
).sum()


erros = (
    teste["resultado"]
    ==
    "ERRO"
).sum()


sem_previsao = (
    teste["resultado"]
    ==
    "SEM_PREVISAO"
).sum()


acuracia = (

    corretos
    /
    (corretos + erros)
    *
    100

)


print("\n")
print("="*70)
print("RESULTADO")
print("="*70)

print(resumo)


print("\nAcurácia:")
print(
    round(acuracia,2),
    "%"
)


# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

os.makedirs(
    "resultados",
    exist_ok=True
)


teste.to_csv(
    SAIDA,
    index=False,
    encoding="utf-8-sig"
)


resumo_final = pd.DataFrame({

    "indicador":[

        "amostra_teste",
        "corretos",
        "erros",
        "sem_previsao",
        "acuracia_percentual"

    ],

    "valor":[

        len(teste),
        corretos,
        erros,
        sem_previsao,
        round(acuracia,2)

    ]

})


resumo_final.to_csv(
    RESUMO,
    index=False,
    encoding="utf-8-sig"
)


print("\nArquivos:")

print(SAIDA)

print(RESUMO)


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