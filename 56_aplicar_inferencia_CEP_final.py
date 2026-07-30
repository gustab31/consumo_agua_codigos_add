# ============================================================
# 56_aplicar_inferencia_CEP_final.py
#
# Aplicação final da inferência de setor por CEP dominante
#
# Mantém:
#   - CD_SETOR original
#   - CD_SETOR inferido
#   - método
#   - confiança
#
# ============================================================

import os
import time
import pandas as pd

inicio = time.time()

print("="*70)
print("APLICAÇÃO FINAL DA INFERÊNCIA POR CEP")
print("="*70)


# ------------------------------------------------------------
# arquivos
# ------------------------------------------------------------

ENTRADA = "resultados/base_inferencia_espacial_setor_v1.csv"

VALIDACAO = "resultados/validacao_regra_CEP.csv"

SAIDA = "resultados/base_setor_final_CEP.csv"

RESUMO = "resultados/resumo_setor_final_CEP.csv"


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


# ------------------------------------------------------------
# criar colunas finais
# ------------------------------------------------------------

df["CD_SETOR_FINAL"] = df["CD_SETOR"]

df["metodo_atribuicao"] = (
    df["CD_SETOR"]
    .notna()
    .map(
        {
            True:
            "OBSERVADO",

            False:
            "SEM_IDENTIFICACAO"
        }
    )
)

df["confianca"] = (
    df["CD_SETOR"]
    .notna()
    .map(
        {
            True:
            1.0,

            False:
            0.0
        }
    )
)


# ------------------------------------------------------------
# criar regra CEP usando todos os observados
# ------------------------------------------------------------

print("\nCriando tabela CEP dominante...")


base_obs = df[
    df["CD_SETOR"].notna()
].copy()


cep_setor = (

    base_obs
    .groupby(
        [
            "CEP",
            "CD_SETOR"
        ]
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
        "CEP"
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
        "CD_SETOR_CEP"
    }
)


print(
    "CEPs dominantes:",
    len(cep_dominante)
)


# ------------------------------------------------------------
# aplicar somente sem setor
# ------------------------------------------------------------

print("\nAplicando inferência...")


sem = df[
    df["CD_SETOR"].isna()
].copy()


sem = sem.merge(
    cep_dominante,
    on="CEP",
    how="left"
)


novos = sem[
    "CD_SETOR_CEP"
].notna()


print(
    "Novos setores:",
    novos.sum()
)


sem.loc[
    novos,
    "CD_SETOR_FINAL"
] = sem.loc[
    novos,
    "CD_SETOR_CEP"
]


sem.loc[
    novos,
    "metodo_atribuicao"
] = "CEP_DOMINANTE"


# confiança baseada na validação

sem.loc[
    novos,
    "confianca"
] = 0.9585


sem = sem.drop(
    columns=[
        "CD_SETOR_CEP"
    ],
    errors="ignore"
)


# ------------------------------------------------------------
# juntar
# ------------------------------------------------------------

obs = df[
    df["CD_SETOR"].notna()
].copy()


resultado = pd.concat(
    [
        obs,
        sem
    ],
    ignore_index=True
)


# garantir tipos

resultado["CD_SETOR_FINAL"] = (
    resultado["CD_SETOR_FINAL"]
    .astype("string")
)


# ------------------------------------------------------------
# estatísticas
# ------------------------------------------------------------

total = len(resultado)

com_final = (
    resultado["CD_SETOR_FINAL"]
    .notna()
    .sum()
)


sem_final = (
    resultado["CD_SETOR_FINAL"]
    .isna()
    .sum()
)


cobertura = (

    com_final
    /
    total
    *
    100

)


resumo = pd.DataFrame({

    "indicador":[

        "total_registros",

        "setores_observados",

        "setores_inferidos_CEP",

        "sem_setor_final",

        "cobertura_final_percentual"

    ],

    "valor":[

        total,

        (
            resultado["metodo_atribuicao"]
            ==
            "OBSERVADO"
        ).sum(),

        (
            resultado["metodo_atribuicao"]
            ==
            "CEP_DOMINANTE"
        ).sum(),

        sem_final,

        round(cobertura,2)

    ]

})


print("\n")
print("="*70)
print("RESULTADO FINAL")
print("="*70)

print(resumo)


# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

os.makedirs(
    "resultados",
    exist_ok=True
)


resultado.to_csv(
    SAIDA,
    index=False,
    encoding="utf-8-sig"
)


resumo.to_csv(
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