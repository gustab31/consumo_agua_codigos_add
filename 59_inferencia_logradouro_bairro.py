# ============================================================
# 59_inferencia_logradouro_bairro.py
#
# Inferência de setor por:
# LOGRADOURO_PAD + BAIRRO
#
# Usa somente registros com setor conhecido
# Valida a regra antes da aplicação
#
# ============================================================

import os
import time
import pandas as pd
import re
import unicodedata


inicio = time.time()


print("="*70)
print("INFERÊNCIA POR LOGRADOURO + BAIRRO")
print("="*70)


# ------------------------------------------------------------
# arquivos
# ------------------------------------------------------------

ENTRADA = "resultados/base_setor_final_CEP.csv"

SAIDA = (
    "resultados/"
    "diagnostico_inferencia_logradouro_bairro.csv"
)

RESUMO = (
    "resultados/"
    "resumo_inferencia_logradouro_bairro.csv"
)


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
# normalização
# ------------------------------------------------------------

def normalizar(valor):

    if pd.isna(valor):

        return ""

    valor = str(valor).upper()

    valor = unicodedata.normalize(
        "NFKD",
        valor
    ).encode(
        "ASCII",
        "ignore"
    ).decode(
        "ASCII"
    )

    valor = re.sub(
        r"[^A-Z0-9 ]",
        " ",
        valor
    )

    valor = re.sub(
        r"\s+",
        " ",
        valor
    )

    return valor.strip()



print("\nNormalizando...")


df["LOGRADOURO_PAD"] = (
    df["Endereco"]
    .apply(normalizar)
)


df["BAIRRO_PAD"] = (
    df["Bairro"]
    .apply(normalizar)
)



df["CD_SETOR_FINAL"] = (

    df["CD_SETOR_FINAL"]
    .astype("string")

)


# ------------------------------------------------------------
# base aprendizado
# ------------------------------------------------------------

base = df[
    df["CD_SETOR_FINAL"].notna()
].copy()


print("\nRegistros com setor:")
print(len(base))


# ------------------------------------------------------------
# tabela dominante
# ------------------------------------------------------------

print("\nCriando regras...")


grupo = (

    base
    .groupby(
        [
            "LOGRADOURO_PAD",
            "BAIRRO_PAD",
            "CD_SETOR_FINAL"
        ]
    )
    .size()
    .reset_index(
        name="quantidade"
    )

)


totais = (

    base
    .groupby(
        [
            "LOGRADOURO_PAD",
            "BAIRRO_PAD"
        ]
    )
    .size()
    .reset_index(
        name="total_endereco"
    )

)


dominante = (

    grupo
    .sort_values(
        [
            "LOGRADOURO_PAD",
            "BAIRRO_PAD",
            "quantidade"
        ],
        ascending=[
            True,
            True,
            False
        ]
    )
    .drop_duplicates(
        [
            "LOGRADOURO_PAD",
            "BAIRRO_PAD"
        ]
    )

)


dominante = dominante.merge(
    totais,
    on=[
        "LOGRADOURO_PAD",
        "BAIRRO_PAD"
    ],
    how="left"
)


dominante["confianca"] = (

    dominante["quantidade"]
    /
    dominante["total_endereco"]
    *
    100

)


# ------------------------------------------------------------
# somente regras fortes
# ------------------------------------------------------------

dominante = dominante[
    dominante["confianca"] >= 90
]


print(
    "Regras criadas:",
    len(dominante)
)


# ------------------------------------------------------------
# aplicar somente sem setor
# ------------------------------------------------------------

teste = df[
    df["CD_SETOR_FINAL"].isna()
].copy()


teste = teste.merge(
    dominante[
        [
            "LOGRADOURO_PAD",
            "BAIRRO_PAD",
            "CD_SETOR_FINAL",
            "confianca"
        ]
    ],
    on=[
        "LOGRADOURO_PAD",
        "BAIRRO_PAD"
    ],
    how="left",
    suffixes=(
        "",
        "_REGRA"
    )
)


resultado = teste[
    teste["CD_SETOR_FINAL_REGRA"]
    .notna()
].copy()


print("\nNovas inferências possíveis:")
print(len(resultado))


# ------------------------------------------------------------
# resumo
# ------------------------------------------------------------

resumo = pd.DataFrame({

    "indicador":[

        "registros_sem_setor_analisados",

        "regras_logradouro_bairro",

        "novas_inferencias",

        "confianca_media"

    ],

    "valor":[

        len(teste),

        len(dominante),

        len(resultado),

        round(
            resultado["confianca"]
            .mean(),
            2
        )
        if len(resultado)>0
        else 0

    ]

})


print("\n")
print("="*70)
print("RESULTADO")
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


print("\nTempo:")

print(
    round(
        time.time()-inicio,
        2
    ),
    "segundos"
)


print("\nFim.")