# ============================================================
# 39_diagnostico_prioridade_sem_CD_SETOR_v2.py
#
# DIAGNOSTICO DOS ENDERECOS SEM CD_SETOR
#
# ============================================================


import pandas as pd
import numpy as np
import time
import unicodedata


inicio = time.time()


print("="*60)
print("DIAGNOSTICO PRIORIDADE SEM CD_SETOR - V2")
print("="*60)



# ============================================================
# ARQUIVOS
# ============================================================


ENTRADA = (
    "resultados/"
    "base_residencial_setor_geocode_fila_v1.csv"
)


SAIDA = (
    "resultados/"
    "diagnostico_prioridade_sem_setor_v2.csv"
)


RESUMO = (
    "resultados/"
    "resumo_prioridade_sem_setor_v2.csv"
)



# ============================================================
# NORMALIZAÇÃO
# ============================================================


def normalizar(valor):

    if pd.isna(valor):

        return ""

    valor = str(valor).upper().strip()

    valor = unicodedata.normalize(

        "NFKD",

        valor

    ).encode(

        "ASCII",

        "ignore"

    ).decode(

        "ASCII"

    )

    valor = (

        valor

        .replace("  "," ")

    )

    return valor



# ============================================================
# LEITURA
# ============================================================


print("\nLendo base...")


df = pd.read_csv(

    ENTRADA,

    low_memory=False

)



print(

    "Shape:",

    df.shape

)



# ============================================================
# FILTRAR SEM SETOR
# ============================================================


sem = df[

    df["CD_SETOR"].isna()

].copy()



print(

    "Sem CD_SETOR:",

    len(sem)

)



# ============================================================
# LOCALIZAR COLUNAS
# ============================================================


if "Endereco" in sem.columns:

    col_end = "Endereco"

elif "endereco" in sem.columns:

    col_end = "endereco"

else:

    raise Exception(
        "Coluna endereco não encontrada"
    )



if "Bairro" in sem.columns:

    col_bairro = "Bairro"

elif "bairro" in sem.columns:

    col_bairro = "bairro"

else:

    raise Exception(
        "Coluna bairro não encontrada"
    )



# ============================================================
# CHAVE ENDEREÇO
# ============================================================


print("\nCriando grupos...")


sem["chave_endereco"] = (

    sem[col_end].apply(normalizar)

    +

    "|"

    +

    sem[col_bairro].apply(normalizar)

)



# ============================================================
# AGRUPAMENTO
# ============================================================


grupo = (

    sem

    .groupby(

        [

            "chave_endereco",

            col_end,

            col_bairro

        ],

        dropna=False

    )

    .size()

    .reset_index(

        name="total_matriculas"

    )

)



# ============================================================
# CLASSIFICAÇÃO
# ============================================================


def prioridade(qtd):

    if qtd >= 30:

        return "MUITO_ALTA"

    elif qtd >= 10:

        return "ALTA"

    elif qtd >= 3:

        return "MEDIA"

    else:

        return "BAIXA"



grupo["prioridade"] = (

    grupo["total_matriculas"]

    .apply(prioridade)

)



grupo = grupo.sort_values(

    "total_matriculas",

    ascending=False

)



# ============================================================
# RESUMO
# ============================================================


resumo = pd.DataFrame({

    "indicador":[

        "matriculas_sem_setor",

        "enderecos_unicos",

        "muito_alta",

        "alta",

        "media",

        "baixa"

    ],

    "valor":[

        len(sem),

        len(grupo),

        (grupo.prioridade=="MUITO_ALTA").sum(),

        (grupo.prioridade=="ALTA").sum(),

        (grupo.prioridade=="MEDIA").sum(),

        (grupo.prioridade=="BAIXA").sum()

    ]

})



print("\n")

print("="*60)

print("RESULTADO")

print("="*60)

print(resumo)



print("\nTop 30:")

print(

    grupo.head(30)

)



# ============================================================
# SALVAR
# ============================================================


grupo.to_csv(

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