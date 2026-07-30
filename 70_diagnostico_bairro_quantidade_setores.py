# ============================================================
# 70_diagnostico_bairro_quantidade_setores.py
#
# Diagnóstico:
# Estrutura bairro x setor censitário
#
# Não faz inferência.
# Mede fragmentação dos bairros.
#
# ============================================================

import pandas as pd
import os
import unicodedata
import re
import time


inicio = time.time()


print("="*70)
print("DIAGNÓSTICO BAIRRO X SETORES")
print("="*70)



ARQUIVO = (
    "resultados/"
    "base_setor_final_CEP.csv"
)


PASTA = "resultados"



# ------------------------------------------------------------
# normalização
# ------------------------------------------------------------

def normalizar(valor):

    if pd.isna(valor):

        return ""

    valor = str(valor).upper()


    valor = (
        unicodedata
        .normalize(
            "NFKD",
            valor
        )
        .encode(
            "ASCII",
            "ignore"
        )
        .decode(
            "ASCII"
        )
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



# ------------------------------------------------------------
# leitura
# ------------------------------------------------------------

print("\nLendo base...")


df = pd.read_csv(

    ARQUIVO,

    low_memory=False

)



print(
    "Registros:",
    len(df)
)



# ------------------------------------------------------------
# setor
# ------------------------------------------------------------

if "CD_SETOR_FINAL" in df.columns:

    campo_setor = "CD_SETOR_FINAL"

elif "CD_SETOR" in df.columns:

    campo_setor = "CD_SETOR"

else:

    raise Exception(
        "Campo de setor não encontrado"
    )



# ------------------------------------------------------------
# somente conhecidos
# ------------------------------------------------------------

df = df[

    df[campo_setor].notna()

].copy()



print(
    "Registros com setor:",
    len(df)
)



# ------------------------------------------------------------
# bairro
# ------------------------------------------------------------

print("\nNormalizando bairros...")


df["BAIRRO_NORM"] = (

    df["Bairro"]

    .apply(normalizar)

)



df = df[

    df["BAIRRO_NORM"] != ""

]



# ------------------------------------------------------------
# distribuição bairro/setor
# ------------------------------------------------------------

print("\nCalculando distribuição...")


dist = (

    df

    .groupby(

        [

            "BAIRRO_NORM",

            campo_setor

        ]

    )

    .size()

    .reset_index(

        name="quantidade"

    )

)



totais = (

    dist

    .groupby(

        "BAIRRO_NORM"

    )

    ["quantidade"]

    .sum()

    .reset_index(

        name="total_bairro"

    )

)



dist = dist.merge(

    totais,

    on="BAIRRO_NORM",

    how="left"

)



dist["percentual_bairro"] = (

    dist["quantidade"]

    /

    dist["total_bairro"]

    *

    100

)



dist = dist.sort_values(

    [

        "BAIRRO_NORM",

        "quantidade"

    ],

    ascending=[

        True,

        False

    ]

)



# ------------------------------------------------------------
# resumo por bairro
# ------------------------------------------------------------

bairro = (

    dist

    .groupby(

        "BAIRRO_NORM"

    )

    .agg(

        setores_distintos=(

            campo_setor,

            "nunique"

        ),

        registros=(

            "quantidade",

            "sum"

        ),

        maior_setor_percentual=(

            "percentual_bairro",

            "max"

        )

    )

    .reset_index()

)



# ------------------------------------------------------------
# classificação
# ------------------------------------------------------------

bairro["classe"] = "FRAGMENTADO"



bairro.loc[

    bairro["setores_distintos"] == 1,

    "classe"

] = "UNICO_SETOR"



bairro.loc[

    (

        bairro["maior_setor_percentual"] >= 80

    ),

    "classe"

] = "DOMINANTE"



# ------------------------------------------------------------
# resumo geral
# ------------------------------------------------------------

resumo = pd.DataFrame({

    "indicador":[

        "bairros_analisados",

        "bairros_com_1_setor",

        "bairros_dominantes_80",

        "bairros_fragmentados",

        "maior_percentual_dominio"

    ],

    "valor":[

        len(bairro),

        (

            bairro["setores_distintos"] == 1

        ).sum(),

        (

            bairro["classe"] == "DOMINANTE"

        ).sum(),

        (

            bairro["classe"] == "FRAGMENTADO"

        ).sum(),

        bairro["maior_setor_percentual"].max()

    ]

})



# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

os.makedirs(

    PASTA,

    exist_ok=True

)



bairro.to_csv(

    PASTA +

    "/diagnostico_bairro_quantidade_setores.csv",

    index=False,

    encoding="utf-8-sig"

)



dist.to_csv(

    PASTA +

    "/diagnostico_bairro_distribuicao_setor.csv",

    index=False,

    encoding="utf-8-sig"

)



resumo.to_csv(

    PASTA +

    "/resumo_bairro_setores.csv",

    index=False,

    encoding="utf-8-sig"

)



print("\n")
print("="*70)
print("RESULTADO")
print("="*70)


print(resumo)



print("\nArquivos:")

print(
    "resultados/diagnostico_bairro_quantidade_setores.csv"
)

print(
    "resultados/diagnostico_bairro_distribuicao_setor.csv"
)

print(
    "resultados/resumo_bairro_setores.csv"
)



print("\nTempo:")

print(

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim.")