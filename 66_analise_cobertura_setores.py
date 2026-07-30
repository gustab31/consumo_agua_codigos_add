# ============================================================
# 66_analise_cobertura_setores.py
#
# Diagnóstico da cobertura dos setores conhecidos
#
# Não faz inferência.
# Analisa onde existe referência.
#
# ============================================================

import pandas as pd
import os
import time
import unicodedata
import re


inicio = time.time()


print("="*70)
print("ANÁLISE DE COBERTURA DOS SETORES OBSERVADOS")
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

        r"[^A-Z0-9]",

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
# campo setor
# ------------------------------------------------------------

if "CD_SETOR_FINAL" in df.columns:

    setor = "CD_SETOR_FINAL"

elif "CD_SETOR" in df.columns:

    setor = "CD_SETOR"

else:

    raise Exception(
        "Campo setor não encontrado"
    )



# ------------------------------------------------------------
# separar
# ------------------------------------------------------------

com = df[

    df[setor].notna()

].copy()


sem = df[

    df[setor].isna()

].copy()



print(

    "Com setor:",

    len(com)

)


print(

    "Sem setor:",

    len(sem)

)



# ------------------------------------------------------------
# normalizar
# ------------------------------------------------------------

for tabela in [

    com,

    sem

]:

    for campo in [

        "Endereco",

        "Bairro"

    ]:

        if campo in tabela.columns:

            tabela[campo+"_NORM"] = (

                tabela[campo]

                .apply(normalizar)

            )



# ------------------------------------------------------------
# resumo setores
# ------------------------------------------------------------

print("\nAnalisando setores...")


por_setor = (

    com

    .groupby(setor)

    .size()

    .reset_index(

        name="quantidade"

    )

    .sort_values(

        "quantidade",

        ascending=False

    )

)



# ------------------------------------------------------------
# bairros
# ------------------------------------------------------------

por_bairro = (

    com

    .groupby(

        "Bairro_NORM"

    )

    [setor]

    .nunique()

    .reset_index(

        name="setores_conhecidos"

    )

)



por_bairro["registros_com_setor"] = (

    com

    .groupby(

        "Bairro_NORM"

    )

    .size()

    .values

)



# ------------------------------------------------------------
# bairros sem setor
# ------------------------------------------------------------

bairro_sem = (

    sem

    .groupby(

        "Bairro_NORM"

    )

    .size()

    .reset_index(

        name="sem_setor"

    )

)



bairro_comparacao = bairro_sem.merge(

    por_bairro,

    on="Bairro_NORM",

    how="left"

)



# ------------------------------------------------------------
# logradouros
# ------------------------------------------------------------

logradouro = (

    com

    .groupby(

        "Endereco_NORM"

    )

    [setor]

    .nunique()

    .reset_index(

        name="setores_logradouro"

    )

)



logradouro["registros"] = (

    com

    .groupby(

        "Endereco_NORM"

    )

    .size()

    .values

)



# ------------------------------------------------------------
# resumo geral
# ------------------------------------------------------------

resumo = pd.DataFrame({

    "indicador":[

        "total_registros",

        "com_setor",

        "sem_setor",

        "setores_distintos",

        "bairros_com_setor",

        "logradouros_com_setor"

    ],

    "valor":[

        len(df),

        len(com),

        len(sem),

        com[setor].nunique(),

        com["Bairro_NORM"].nunique(),

        com["Endereco_NORM"].nunique()

    ]

})



print("\n")
print("="*70)
print("RESUMO")
print("="*70)


print(resumo)



# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

os.makedirs(

    PASTA,

    exist_ok=True

)



por_setor.to_csv(

    PASTA +

    "/cobertura_por_setor.csv",

    index=False,

    encoding="utf-8-sig"

)



bairro_comparacao.to_csv(

    PASTA +

    "/cobertura_bairro_setor.csv",

    index=False,

    encoding="utf-8-sig"

)



logradouro.to_csv(

    PASTA +

    "/cobertura_logradouro_setor.csv",

    index=False,

    encoding="utf-8-sig"

)



resumo.to_csv(

    PASTA +

    "/resumo_cobertura_setores.csv",

    index=False,

    encoding="utf-8-sig"

)



print("\nArquivos:")

print(

    "resultados/cobertura_por_setor.csv"

)

print(

    "resultados/cobertura_bairro_setor.csv"

)

print(

    "resultados/cobertura_logradouro_setor.csv"

)

print(

    "resultados/resumo_cobertura_setores.csv"

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