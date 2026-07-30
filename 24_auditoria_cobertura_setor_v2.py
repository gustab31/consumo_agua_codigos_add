# ============================================================
# 24_auditoria_cobertura_setor_v2.py
#
# Auditoria após propagação de CD_SETOR
#
# ============================================================


import pandas as pd
import os
import time


inicio = time.time()


print("="*60)
print("AUDITORIA DE COBERTURA CD_SETOR - V2")
print("="*60)



ARQ_BASE = (
    "resultados/"
    "base_residencial_setor_propagado_v2.csv"
)


SAIDA_RESUMO = (
    "resultados/"
    "auditoria_cobertura_setor_v2.csv"
)


SAIDA_FILA = (
    "resultados/"
    "fila_proxima_geocodificacao.csv"
)



if not os.path.exists(ARQ_BASE):

    raise FileNotFoundError(ARQ_BASE)



# ============================================================
# LEITURA
# ============================================================


print("\nLendo base...")


df = pd.read_csv(

    ARQ_BASE,

    low_memory=False

)


print(

    "Shape:",

    df.shape

)



# ============================================================
# IDENTIFICAR COLUNAS
# ============================================================


def coluna(df, lista):

    for c in lista:

        if c in df.columns:

            return c

    return None



endereco = coluna(

    df,

    [
        "Endereco",
        "endereco"
    ]

)


bairro = coluna(

    df,

    [
        "Bairro",
        "bairro"
    ]

)



if endereco is None or bairro is None:

    raise Exception(
        "Colunas de endereço não encontradas"
    )



# ============================================================
# RESUMO GERAL
# ============================================================


print("\nCalculando cobertura...")


total = len(df)


com_setor = df["CD_SETOR"].notna().sum()


sem_setor = total - com_setor



# endereços únicos


df["_END"] = (

    df[endereco]

    .astype(str)

    .str.upper()

    .str.strip()

)


df["_BAIRRO"] = (

    df[bairro]

    .astype(str)

    .str.upper()

    .str.strip()

)



enderecos_total = (

    df[

        [

            "_END",

            "_BAIRRO"

        ]

    ]

    .drop_duplicates()

    .shape[0]

)



enderecos_com_setor = (

    df[

        df["CD_SETOR"].notna()

    ]

    [

        [

            "_END",

            "_BAIRRO"

        ]

    ]

    .drop_duplicates()

    .shape[0]

)



enderecos_sem_setor = (

    enderecos_total -

    enderecos_com_setor

)



resumo = pd.DataFrame({

    "indicador":[

        "total_matriculas",

        "com_CD_SETOR",

        "sem_CD_SETOR",

        "percentual_cobertura",

        "enderecos_unicos",

        "enderecos_com_setor",

        "enderecos_sem_setor"

    ],

    "valor":[

        total,

        com_setor,

        sem_setor,

        round(

            com_setor/total*100,

            2

        ),

        enderecos_total,

        enderecos_com_setor,

        enderecos_sem_setor

    ]

})



print(resumo)



# ============================================================
# GRUPOS SEM SETOR
# ============================================================


print("\nCriando fila...")


sem = df[

    df["CD_SETOR"].isna()

].copy()



fila = (

    sem

    .groupby(

        [

            "_END",

            "_BAIRRO"

        ]

    )

    .agg(

        total_matriculas=(

            "MATRICULA",

            "count"

        ),

        matriculas=(

            "MATRICULA",

            lambda x:

            ";".join(

                x.astype(str)

            )

        )

    )

    .reset_index()

)



# recuperar nomes originais


fila = fila.rename(

    columns={

        "_END":"endereco",

        "_BAIRRO":"bairro"

    }

)



# ============================================================
# PRIORIDADE
# ============================================================


def prioridade(n):

    if n >= 100:

        return "MUITO_ALTA"

    elif n >= 30:

        return "ALTA"

    elif n >= 10:

        return "MEDIA"

    else:

        return "BAIXA"



fila["prioridade"] = (

    fila["total_matriculas"]

    .apply(prioridade)

)



fila = fila.sort_values(

    [

        "total_matriculas"

    ],

    ascending=False

)



# ============================================================
# SALVAR
# ============================================================


resumo.to_csv(

    SAIDA_RESUMO,

    index=False,

    encoding="utf-8-sig"

)



fila.to_csv(

    SAIDA_FILA,

    index=False,

    encoding="utf-8-sig"

)



print("\n")

print("="*60)

print("RESULTADO")

print("="*60)


print(

    "Matrículas sem setor:",

    sem_setor

)


print(

    "Endereços sem setor:",

    enderecos_sem_setor

)


print("\nTop grupos:")

print(

    fila.head(20)

)



print("\nArquivos:")

print(SAIDA_RESUMO)

print(SAIDA_FILA)



print("\nTempo:")

print(

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim.")