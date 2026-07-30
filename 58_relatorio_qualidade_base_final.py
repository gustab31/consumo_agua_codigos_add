# ============================================================
# 58_relatorio_qualidade_base_final.py
#
# Relatório final da qualidade da identificação de setores
#
# Gera:
#   - distribuição por método
#   - cobertura geral
#   - análise por bairro
#   - confiança das inferências
#
# ============================================================

import os
import time
import pandas as pd


inicio = time.time()


print("="*70)
print("RELATÓRIO DE QUALIDADE DA BASE FINAL")
print("="*70)


# ------------------------------------------------------------
# arquivos
# ------------------------------------------------------------

ENTRADA = "resultados/base_setor_final_CEP.csv"

PASTA = "resultados"


SAIDA_METODO = (
    f"{PASTA}/relatorio_metodo_atribuicao.csv"
)

SAIDA_BAIRRO = (
    f"{PASTA}/relatorio_bairro_setor.csv"
)

SAIDA_CONFIANCA = (
    f"{PASTA}/relatorio_confianca_final.csv"
)

SAIDA_RESUMO = (
    f"{PASTA}/relatorio_geral_base_final.csv"
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
# padronização
# ------------------------------------------------------------

df["CD_SETOR_FINAL"] = (

    df["CD_SETOR_FINAL"]
    .astype("string")

)


df["metodo_atribuicao"] = (

    df["metodo_atribuicao"]
    .astype("string")

)



# ------------------------------------------------------------
# resumo método
# ------------------------------------------------------------

print("\nGerando método de atribuição...")


metodo = (

    df["metodo_atribuicao"]
    .value_counts(dropna=False)
    .reset_index()

)


metodo.columns = [

    "metodo",

    "quantidade"

]


metodo["percentual"] = (

    metodo["quantidade"]
    /
    len(df)
    *
    100

).round(2)



# ------------------------------------------------------------
# bairros
# ------------------------------------------------------------

print("\nGerando análise por bairro...")


if "Bairro" in df.columns:


    bairro = (

        df
        .groupby(
            "Bairro",
            dropna=False
        )
        .agg(

            registros=(
                "Bairro",
                "size"
            ),

            com_setor=(
                "CD_SETOR_FINAL",
                lambda x:
                x.notna().sum()
            ),

            inferidos=(
                "metodo_atribuicao",
                lambda x:
                (
                    x
                    ==
                    "CEP_DOMINANTE"
                )
                .sum()
            )

        )
        .reset_index()

    )


    bairro["sem_setor"] = (

        bairro["registros"]

        -

        bairro["com_setor"]

    )


    bairro["cobertura_percentual"] = (

        bairro["com_setor"]

        /

        bairro["registros"]

        *

        100

    ).round(2)


else:

    bairro = pd.DataFrame()



# ------------------------------------------------------------
# confiança
# ------------------------------------------------------------

print("\nGerando confiança...")


if "confianca" in df.columns:


    confianca = (

        df["confianca"]
        .value_counts(dropna=False)
        .reset_index()

    )

    confianca.columns = [

        "valor_confianca",

        "quantidade"

    ]


else:

    confianca = pd.DataFrame()



# ------------------------------------------------------------
# resumo geral
# ------------------------------------------------------------

total = len(df)


com_setor = (

    df["CD_SETOR_FINAL"]
    .notna()
    .sum()

)


sem_setor = total - com_setor


inferidos = (

    df["metodo_atribuicao"]
    ==
    "CEP_DOMINANTE"

).sum()


observados = (

    df["metodo_atribuicao"]
    ==
    "OBSERVADO"

).sum()



resumo = pd.DataFrame({

    "indicador":[

        "total_registros",

        "setores_observados",

        "setores_inferidos_CEP",

        "sem_setor",

        "cobertura_final_percentual"

    ],

    "valor":[

        total,

        observados,

        inferidos,

        sem_setor,

        round(
            com_setor / total * 100,
            2
        )

    ]

})


print("\n")
print("="*70)
print("RESUMO FINAL")
print("="*70)

print(resumo)


# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

os.makedirs(
    PASTA,
    exist_ok=True
)


metodo.to_csv(
    SAIDA_METODO,
    index=False,
    encoding="utf-8-sig"
)


bairro.to_csv(
    SAIDA_BAIRRO,
    index=False,
    encoding="utf-8-sig"
)


confianca.to_csv(
    SAIDA_CONFIANCA,
    index=False,
    encoding="utf-8-sig"
)


resumo.to_csv(
    SAIDA_RESUMO,
    index=False,
    encoding="utf-8-sig"
)


print("\nArquivos:")

print(SAIDA_METODO)

print(SAIDA_BAIRRO)

print(SAIDA_CONFIANCA)

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